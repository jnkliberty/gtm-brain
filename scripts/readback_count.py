#!/usr/bin/env python3
"""Count distinct people per window for an outcome readback. Standard library only.

Usage:
  python3 scripts/readback_count.py --touches brain/crm-export/touches.csv --change brain/changes/<file>.md \
      --today YYYY-MM-DD [--read-date YYYY-MM-DD] [--baseline START:END --candidate START:END]
  python3 scripts/readback_count.py --self-test

Prints JSON. It counts; it decides nothing. The rules in brain/readback-rules.md turn the counts into
a decision. Without --baseline and --candidate, the candidate window holds the outbound touches tagged
with the change ID, and the baseline holds untagged outbound touches on the same channels in the
baseline-days before changed_at (readback-windows). Every threshold comes from the Thresholds section
of brain/readback-rules.md. Reads only; writes nothing.
"""
import argparse
import csv
import datetime
import io
import json
import math
import os
import re
import sys
import tempfile
from fractions import Fraction

# The thresholds live only in the Thresholds section of brain/readback-rules.md, one per line as
# "- threshold <name>: <whole number>". thresholds() reads them; a missing or doubled name stops the run.
RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "brain", "readback-rules.md")
THRESHOLDS = ("lift-points", "guard-points", "min-people-difference", "baseline-days", "min-delivered-people",
              "open-window-days")
POSITIVE = {"interest", "question", "referral"}
CLASSES = ("interest", "question", "referral", "rejection", "opt-out", "auto-reply")
COLUMNS = ["touch_id", "contact_id", "company_id", "company_domain", "email", "linkedin_url", "channel",
           "direction", "play", "change_id", "sent_at", "delivery_status", "replied_at", "reply_class",
           "meeting_booked_at", "sender", "source"]


def day(text):
    try:
        return datetime.date.fromisoformat((text or "").strip())
    except ValueError:
        return None


def front(path):
    """The frontmatter of a change record as a dict of strings."""
    with open(path, encoding="utf-8") as f:
        m = re.match(r"---\n(.*?)\n---", f.read(), re.S)
    return dict(re.findall(r"(?m)^(\w+):[ \t]*(.*?)\s*$", m.group(1))) if m else {}


def person(row):
    """readback-people: contact_id, then email, then LinkedIn URL. None when the row names nobody."""
    for key in ("contact_id", "email", "linkedin_url"):
        value = (row.get(key) or "").strip()
        if value:
            # A CRM ID is case-sensitive; an email or URL is not.
            return f"{key}:{value if key == 'contact_id' else value.lower()}"
    return None


def dated(touch, key, problems):
    """True when the field holds a valid date. A non-blank invalid value is a problem and counts as no date."""
    value = touch[key].strip()
    if value and not day(value):
        problems.append(f"{touch['touch_id']}: {key} {value!r} is not a YYYY-MM-DD date; not counted")
    return bool(day(value))


def thresholds(path=RULES):
    """The numbers in the Thresholds section of the rules file. Exits with a clear message when one is missing."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise SystemExit(f"cannot read the rules file {path}: {e.strerror}")
    # Only the "## Thresholds" section counts; a threshold line anywhere else is ignored.
    # The section ends at the next level 1 or 2 heading, whatever whitespace follows the hashes.
    section = re.search(r"(?ms)^##[ \t]+Thresholds[ \t]*\n(.*?)(?=^#{1,2}[ \t]|\Z)", text)
    if not section:
        raise SystemExit(f"{path}: no '## Thresholds' section")
    # Every threshold line is read, whatever its value; duplicates are judged first, then each value.
    found = re.findall(r"(?m)^- threshold ([a-z-]+):[ \t]*(.*?)[ \t]*$", section.group(1))
    names = [name for name, _ in found]
    for name in names:
        if names.count(name) > 1:
            raise SystemExit(f"{path}: threshold {name} appears {names.count(name)} times; keep one line")
    values = {}
    for name, number in found:
        top = 100 if name.endswith("-points") else 3650
        if not re.fullmatch(r"\d+", number) or not 1 <= int(number) <= top:
            raise SystemExit(f"{path}: threshold {name} is {number!r}; use a whole number from 1 to {top}")
        values[name] = int(number)
    missing = [n for n in THRESHOLDS if n not in values]
    if missing:
        raise SystemExit(f"{path}: no line '- threshold <name>: <whole number>' for {', '.join(missing)}")
    return values


def compare(baseline, candidate, threshold, min_people):
    """Exact differences (candidate minus baseline) from the counts, and the threshold tests.

    people_difference: the candidate count minus the count the baseline rate predicts for the candidate's
    delivered people. A side (above or below) passes only when both the points and the people difference
    reach their thresholds; *_points_only is true when the points reach it and the people difference does not."""
    if not baseline["of"] or not candidate["of"]:
        return {"points": None, "people_difference": None, "at_or_above": None, "at_or_below": None,
                "above_points_only": None, "below_points_only": None}
    diff = 100 * (Fraction(candidate["people"], candidate["of"]) - Fraction(baseline["people"], baseline["of"]))
    people = candidate["people"] - Fraction(baseline["people"] * candidate["of"], baseline["of"])
    enough = abs(people) >= min_people
    above, below = diff >= threshold, diff <= -threshold
    # Shown values are cut toward zero, never rounded up, so a value under a threshold never shows as reaching it.
    return {"points": math.trunc(diff * 10**6) / 10**6, "people_difference": math.trunc(people * 10**6) / 10**6,
            "at_or_above": above and enough, "at_or_below": below and enough,
            "above_points_only": above and not enough, "below_points_only": below and not enough}


def window_stats(rows, start, end, problems):
    people, delivered, replied, positive, meetings, unclassified = {}, set(), set(), set(), set(), set()
    by_class = {c: set() for c in CLASSES}
    senders, sources, channels, sent_days = set(), set(), set(), []
    for r in rows:
        who = person(r)
        people.setdefault(who, []).append(r)
        senders.add(r["sender"].strip())
        sources.add(r["source"].strip())
        channels.add(r["channel"].strip())
        sent_days.append(r["sent_at"].strip())
    for who, touches in people.items():
        if all(t["delivery_status"].strip() == "bounced" for t in touches):
            continue
        delivered.add(who)
        for t in touches:
            cls = t["reply_class"].strip()
            if cls in by_class:
                by_class[cls].add(who)
            reply_dated = dated(t, "replied_at", problems)
            if reply_dated and not cls:
                unclassified.add(who)
            if (cls and cls != "auto-reply") or (reply_dated and not cls):
                replied.add(who)
            if cls in POSITIVE:
                positive.add(who)
            if dated(t, "meeting_booked_at", problems):
                meetings.add(who)
    n = len(delivered)

    def rate(found):
        return {"people": len(found), "of": n, "percent": round(100 * len(found) / n, 1) if n else None}

    return {"start": start.isoformat() if start else None, "end": end.isoformat() if end else None,
            "outbound_touches": len(rows), "people_sent": len(people),
            "people_bounced_only": len(people) - n, "people_delivered": n,
            "replied_by_class": {c: len(s) for c, s in by_class.items()} | {"unclassified": len(unclassified)},
            "rates": {"reply-rate": rate(replied), "positive-reply-rate": rate(positive),
                      "meeting-rate": rate(meetings), "opt-out-rate": rate(by_class["opt-out"])},
            "first_sent": min(sent_days) if sent_days else None, "last_sent": max(sent_days) if sent_days else None,
            "senders": sorted(senders), "sources": sorted(sources), "channels": sorted(channels)}


def span(text):
    start, _, end = (text or "").partition(":")
    a, b = day(start), day(end)
    if not a or not b or b < a:
        raise SystemExit(f"bad window {text!r}: use START:END as YYYY-MM-DD:YYYY-MM-DD")
    return a, b


def count(touches_path, change_path, today, read_date=None, baseline=None, candidate=None, limits=None):
    limits = limits or thresholds()
    out = {"touches": touches_path, "today": today.isoformat(), "thresholds": limits, "problems": []}
    if not os.path.isfile(touches_path):
        return out | {"export_missing": True}
    with open(touches_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        header = reader.fieldnames or []
    if header != COLUMNS:
        out["problems"].append(f"columns differ from the contract: {header}")
        missing = [c for c in COLUMNS if c not in header]
        if missing:
            return out | {"export_missing": False, "unreadable_columns": missing}
    out["export_missing"] = False
    out["read_date"] = read_date.isoformat() if read_date else None
    out["export_age_days"] = (today - read_date).days if read_date else None
    rec = front(change_path) if change_path and os.path.isfile(change_path) else {}
    change_id = rec.get("change_id", "")
    out["change"] = {k: rec.get(k, "") for k in ("change_id", "changed_at", "primary_metric", "declared_at")}
    out["change"]["record_found"] = bool(rec)
    outbound, unnamed = [], []  # unnamed: a valid send with no person; not counted, but still a send date
    for r in rows:
        if r["direction"].strip() != "outbound":
            out.setdefault("not_outbound_rows", []).append(r["touch_id"])
            continue
        if not day(r["sent_at"]) or not person(r):
            out["problems"].append(f"{r['touch_id']}: no valid sent_at or no person; not counted")
            if day(r["sent_at"]):
                unnamed.append(r)
            continue
        outbound.append(r)

    def in_candidate(r):
        if candidate:
            return candidate[0] <= day(r["sent_at"]) <= candidate[1]
        return bool(change_id) and r["change_id"].strip() == change_id
    c_rows = [r for r in outbound if in_candidate(r)]
    send_days = sorted(day(r["sent_at"]) for r in c_rows + [u for u in unnamed if in_candidate(u)])
    if candidate:
        c_start, c_end = candidate
    else:
        c_start, c_end = (send_days[0], send_days[-1]) if send_days else (None, None)
    if baseline:
        b_start, b_end = baseline
        b_rows = [r for r in outbound if b_start <= day(r["sent_at"]) <= b_end]
    else:
        changed = day(rec.get("changed_at"))
        b_start = changed - datetime.timedelta(days=limits["baseline-days"]) if changed else None
        b_end = changed - datetime.timedelta(days=1) if changed else None
        channels = {r["channel"].strip() for r in c_rows}
        b_rows = [r for r in outbound if changed and not r["change_id"].strip()
                  and r["channel"].strip() in channels and b_start <= day(r["sent_at"]) <= b_end]
    out["windows"] = {"baseline": window_stats(b_rows, b_start, b_end, out["problems"]),
                      "candidate": window_stats(c_rows, c_start, c_end, out["problems"])}
    # Reported candidate send dates include sends with no person, in every mode.
    out["windows"]["candidate"]["first_sent"] = send_days[0].isoformat() if send_days else None
    out["windows"]["candidate"]["last_sent"] = send_days[-1].isoformat() if send_days else None
    b_rates, c_rates = out["windows"]["baseline"]["rates"], out["windows"]["candidate"]["rates"]
    # readback-lift, readback-guard, readback-min-difference: exact count ratios; percents are for display only.
    few = limits["min-people-difference"]
    out["comparison"] = {m: compare(b_rates[m], c_rates[m], limits["lift-points"], few)
                         for m in ("reply-rate", "positive-reply-rate", "meeting-rate")}
    guard = compare(b_rates["opt-out-rate"], c_rates["opt-out-rate"], limits["guard-points"], few)
    out["comparison"]["opt-out-rate"] = guard
    out["guard_worse"] = guard["at_or_above"]
    metric = rec.get("primary_metric", "")
    primary = out["comparison"].get(metric) if metric != "opt-out-rate" else None
    out["lift"] = None if not primary or primary["points"] is None else (
        "win" if primary["at_or_above"] else "loss" if primary["at_or_below"] else "neither")
    # Points met by too few people: the readback-decide line for readback-min-difference reads this list.
    thin = [(metric, primary)] if primary and (primary["above_points_only"] or primary["below_points_only"]) else []
    thin += [("opt-out-rate", guard)] if guard["above_points_only"] else []
    out["too_few_people"] = [f"{m}: {c['points']} points, but a people difference of {c['people_difference']}, "
                             f"under {few}" for m, c in thin]
    # Overlap: another change ID on any outbound touch sent inside the candidate window.
    others = set()
    if c_start:
        others = {r["change_id"].strip() for r in outbound if r["change_id"].strip()
                  and r["change_id"].strip() != change_id and c_start <= day(r["sent_at"]) <= c_end}
    if change_path and os.path.isdir(os.path.dirname(change_path) or "."):
        folder = os.path.dirname(change_path) or "."
        for name in sorted(os.listdir(folder)):
            other = front(os.path.join(folder, name)) if name.endswith(".md") else {}
            when = day(other.get("changed_at"))
            if other.get("change_id") and other["change_id"] != change_id and when and c_start and c_start <= when <= c_end:
                others.add(other["change_id"])
    out["overlapping_change_ids"] = sorted(others)
    # First and last candidate sends include rows with no person (readback-confounders, readback-declared).
    first, last = (send_days[0], send_days[-1]) if send_days else (None, None)
    out["days_since_last_candidate_send"] = (today - last).days if last else None
    # readback-confounders (open window) and readback-min-volume, against the rules-file thresholds.
    out["window_open"] = bool(last) and (today - last).days < limits["open-window-days"]
    out["min_volume_met"] = all(w["people_delivered"] >= limits["min-delivered-people"] for w in out["windows"].values())
    declared = day(rec.get("declared_at"))
    out["declared_on_or_before_first_touch"] = bool(declared and first and declared <= first)
    out["counted_rows"] = len(c_rows) + len(b_rows)
    return out


def self_test():
    rows = [
        # baseline: p1 replies twice (one person), p2 bounces only, p3 bounces then delivers
        ["b1", "c1", "", "", "", "", "email", "outbound", "x", "", "2026-09-10", "delivered", "2026-09-11", "interest", "2026-09-15", "s", "v"],
        ["b2", "c1", "", "", "", "", "email", "outbound", "x", "", "2026-09-12", "delivered", "2026-09-13", "interest", "", "s", "v"],
        ["b3", "c2", "", "", "", "", "email", "outbound", "x", "", "2026-09-10", "bounced", "", "", "", "s", "v"],
        ["b4", "c3", "", "", "", "", "email", "outbound", "x", "", "2026-09-10", "bounced", "", "", "", "s", "v"],
        ["b5", "c3", "", "", "", "", "email", "outbound", "x", "", "2026-09-14", "sent", "2026-09-15", "opt-out", "", "s", "v"],
        # candidate: tagged; one auto-reply; one inbound row and one other change inside the window
        ["k1", "c4", "", "", "", "", "email", "outbound", "x", "chg", "2026-10-02", "delivered", "2026-10-03", "auto-reply", "", "s2", "v"],
        ["k2", "", "", "", "Ann@D.example", "", "email", "outbound", "x", "chg", "2026-10-03", "delivered", "2026-10-04", "question", "", "s", "v"],
        ["i1", "c9", "", "", "", "", "other", "inbound", "", "", "2026-10-03", "unknown", "", "interest", "", "", "form"],
        ["o1", "c8", "", "", "", "", "email", "outbound", "x", "other-chg", "2026-10-02", "delivered", "", "", "", "s", "v"],
    ]
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows([COLUMNS] + rows)
    with tempfile.TemporaryDirectory() as tmp:
        touches = os.path.join(tmp, "touches.csv")
        for name in (touches, os.path.join(tmp, "base.csv")):
            with open(name, "w", encoding="utf-8") as f:
                f.write(buf.getvalue())
        changes = os.path.join(tmp, "changes")
        os.mkdir(changes)
        rec = os.path.join(changes, "2026-10-01-chg.md")
        with open(rec, "w", encoding="utf-8") as f:
            f.write("---\nchange_id: chg\nchanged_at: 2026-10-01\nwhat_changed: x\nprimary_metric: reply-rate\n"
                    "declared_at: 2026-10-02\nowner: Sam\n---\n")
        r = count(touches, rec, datetime.date(2026, 10, 30), datetime.date(2026, 10, 20))
        b, c = r["windows"]["baseline"], r["windows"]["candidate"]
        checks = [
            (b["people_sent"], 3), (b["people_delivered"], 2), (b["people_bounced_only"], 1),
            (b["rates"]["reply-rate"]["people"], 2), (b["rates"]["positive-reply-rate"]["people"], 1),
            (b["rates"]["opt-out-rate"]["percent"], 50.0), (b["rates"]["meeting-rate"]["people"], 1),
            (c["people_delivered"], 2), (c["rates"]["reply-rate"]["people"], 1),
            (c["replied_by_class"]["auto-reply"], 1), (c["senders"], ["s", "s2"]),
            (r["not_outbound_rows"], ["i1"]), (r["overlapping_change_ids"], ["other-chg"]),
            (r["declared_on_or_before_first_touch"], True), (r["export_age_days"], 10),
            (r["days_since_last_candidate_send"], 27), (b["start"], "2026-09-03"),
        ]
        late = count(touches, rec, datetime.date(2026, 10, 30), None, None, None)
        checks.append((late["export_age_days"], None))
        missing = count(os.path.join(tmp, "none.csv"), rec, datetime.date(2026, 10, 30))
        checks.append((missing["export_missing"], True))
        explicit = count(touches, rec, datetime.date(2026, 10, 30), None,
                         span("2026-09-01:2026-09-30"), span("2026-10-01:2026-10-31"))
        checks.append((explicit["windows"]["candidate"]["people_delivered"], 3))
        # Explicit windows: days since the last counted candidate touch (2026-10-03), not the window end.
        checks.append((explicit["days_since_last_candidate_send"], 27))
        odd = [
            ["x1", "Ab1", "", "", "", "", "email", "outbound", "x", "chg", "2026-10-02", "delivered", "unknown", "", "", "s", "v"],
            ["x2", "ab1", "", "", "", "", "email", "outbound", "x", "chg", "2026-10-02", "delivered", "", "", "unknown", "s", "v"],
            ["x3", "", "", "", "A@B.example", "", "email", "outbound", "x", "chg", "2026-10-02", "delivered", "", "", "", "s", "v"],
            ["x4", "", "", "", "a@b.example", "", "email", "outbound", "x", "chg", "2026-10-03", "delivered", "", "", "", "s", "v"],
            # A candidate send with no person is not counted, but it is still the last send.
            ["x5", "", "", "", "", "", "email", "outbound", "x", "chg", "2026-10-28", "delivered", "", "", "", "s", "v"],
            ["x0", "", "", "", "", "", "email", "outbound", "x", "chg", "2026-10-01", "delivered", "", "", "", "s", "v"],
        ]
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows([COLUMNS] + odd)
        with open(touches, "w", encoding="utf-8") as f:
            f.write(buf.getvalue())
        o = count(touches, rec, datetime.date(2026, 10, 30), datetime.date(2026, 10, 20))
        oc = o["windows"]["candidate"]
        checks += [(oc["people_sent"], 3),  # contact IDs keep their case; emails fold case
                   (oc["rates"]["reply-rate"]["people"], 0), (oc["rates"]["meeting-rate"]["people"], 0),
                   (sum("x1" in p for p in o["problems"]), 1), (sum("x2" in p for p in o["problems"]), 1),
                   (o["days_since_last_candidate_send"], 2), (o["window_open"], True),
                   # Unnamed sends on both sides of the named ones set the reported dates and the window bounds.
                   ((oc["first_sent"], oc["last_sent"], oc["start"], oc["end"]),
                    ("2026-10-01", "2026-10-28", "2026-10-01", "2026-10-28"))]
        # A people difference just under 3 never shows as 3.0: 4 of 10**8+1 against 1 of 10**8 is 2.99999999.
        near = compare({"people": 1, "of": 10**8}, {"people": 4, "of": 10**8 + 1}, 0, 3)
        checks += [(near["people_difference"] < 3, True), (near["above_points_only"], True)]
        # Exact points from counts: 2 of 101 against 0 of 1 is 1.98 points, not the displayed 2.0.
        exact = compare({"people": 0, "of": 1}, {"people": 2, "of": 101}, 2, 0)
        checks += [(exact["points"], 1.980198), (exact["at_or_above"], False), (exact["at_or_below"], False)]
        checks.append((compare({"people": 2, "of": 28}, {"people": 6, "of": 28}, 5, 3)["at_or_above"], True))
        checks.append((compare({"people": 0, "of": 0}, {"people": 6, "of": 28}, 5, 3)["points"], None))
        # readback-min-difference: 3 of 20 against 2 of 20 is 5 points but one person, so no win.
        one = compare({"people": 2, "of": 20}, {"people": 3, "of": 20}, 5, 3)
        checks += [(one["points"], 5.0), (one["people_difference"], 1.0), (one["at_or_above"], False),
                   (one["above_points_only"], True)]
        # The counter itself applies it: reply-rate 1 of 2 against 2 of 2 is -50 points but one person.
        checks += [(r["lift"], "neither"), (len(r["too_few_people"]), 1),
                   (r["comparison"]["reply-rate"]["people_difference"], -1.0)]
        # Opt-outs 3 of 28 against 1 of 28: 7.1 points by two people does not trip the guard.
        g = compare({"people": 1, "of": 28}, {"people": 3, "of": 28}, 2, 3)
        checks += [(g["at_or_above"], False), (g["above_points_only"], True)]
        # Thresholds come from the rules file: the real one parses, an edited one changes the result,
        # and a missing number stops the run with its name.
        real = thresholds()
        checks.append((sorted(real), sorted(THRESHOLDS)))
        checks += [(r["min_volume_met"], False), (r["window_open"], False)]
        rules = os.path.join(tmp, "rules.md")

        def lines(values):
            return "## Thresholds\n\n" + "".join(f"- threshold {k}: {v}\n" for k, v in values.items())

        def edited(**changes):
            with open(rules, "w", encoding="utf-8") as f:
                f.write(lines(real | changes))
            return count(os.path.join(tmp, "base.csv"), rec, datetime.date(2026, 10, 30), None, None, None,
                         thresholds(rules))

        def stops(text):
            with open(rules, "w", encoding="utf-8") as f:
                f.write(text)
            try:
                thresholds(rules)
                return "no error"
            except SystemExit as e:
                return str(e)
        # A threshold line outside the Thresholds section does not count.
        others = {k: v for k, v in real.items() if k != "lift-points"}
        for heading in ("## Appendix", "# Appendix", "##\tAppendix"):
            checks.append(("lift-points" in stops(lines(others) + f"\n{heading}\n\n- threshold lift-points: 99\n"), True))
        # A second, bad line for a name stops the run and names it; it is never skipped.
        checks.append(("lift-points" in stops(lines(real) + "- threshold lift-points: -1\n"), True))
        # Out of range stops the run and names the threshold, for every threshold.
        checks += [(f"threshold {k} is" in stops(lines(real | {k: 999999999})), True) for k in THRESHOLDS]
        checks.append(("baseline-days" in stops(lines(real | {"baseline-days": 0})), True))
        lift = edited(**{"lift-points": 40, "min-people-difference": 1})
        checks += [(lift["thresholds"]["lift-points"], 40), (lift["lift"], "loss"), (lift["too_few_people"], [])]
        checks.append((edited(**{"baseline-days": 10})["windows"]["baseline"]["start"], "2026-09-21"))
        checks.append((edited(**{"min-delivered-people": 2})["min_volume_met"], True))
        checks.append((edited(**{"open-window-days": 30})["window_open"], True))
        gone = stops(lines({"lift-points": 5, "min-people-difference": 3}))
        checks.append((all(n in gone for n in THRESHOLDS if n not in ("lift-points", "min-people-difference")), True))
    bad = [f"check {i}: got {got!r}, want {want!r}" for i, (got, want) in enumerate(checks) if got != want]
    print("self-test " + ("FAILED\n" + "\n".join(bad) if bad else f"passed ({len(checks)} checks)"))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--touches", default="brain/crm-export/touches.csv")
    ap.add_argument("--change", help="the change record, brain/changes/<YYYY-MM-DD>-<change-id>.md")
    ap.add_argument("--today", help="run date, YYYY-MM-DD")
    ap.add_argument("--read-date", help="date the touches export was read, YYYY-MM-DD")
    ap.add_argument("--baseline", help="explicit baseline window START:END")
    ap.add_argument("--candidate", help="explicit candidate window START:END")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    today = day(a.today)
    if not today or (a.read_date and not day(a.read_date)):
        ap.error("--today is required and dates use YYYY-MM-DD")
    if bool(a.baseline) != bool(a.candidate):
        ap.error("give both --baseline and --candidate, or neither")
    if not a.change and not a.candidate:
        ap.error("give --change, or --baseline and --candidate")
    result = count(a.touches, a.change, today, day(a.read_date),
                   span(a.baseline) if a.baseline else None, span(a.candidate) if a.candidate else None)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
