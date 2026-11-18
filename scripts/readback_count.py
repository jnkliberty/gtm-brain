#!/usr/bin/env python3
"""Count distinct people per window for an outcome readback. Standard library only.

Usage:
  python3 scripts/readback_count.py --touches brain/crm-export/touches.csv --change brain/changes/<file>.md \
      --today YYYY-MM-DD [--read-date YYYY-MM-DD] [--baseline START:END --candidate START:END]
  python3 scripts/readback_count.py --self-test

Prints JSON. It counts; it decides nothing. The rules in brain/readback-rules.md turn the counts into
a decision. Without --baseline and --candidate, the candidate window holds the outbound touches tagged
with the change ID, and the baseline holds untagged outbound touches on the same channels in the
28 days before changed_at (readback-windows). Reads only; writes nothing.
"""
import argparse
import csv
import datetime
import io
import json
import os
import re
import sys
import tempfile

BASELINE_DAYS = 28
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
        value = (row.get(key) or "").strip().lower()
        if value:
            return f"{key}:{value}"
    return None


def window_stats(rows, start, end):
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
            if t["replied_at"].strip() and not cls:
                unclassified.add(who)
            if (cls and cls != "auto-reply") or (t["replied_at"].strip() and not cls):
                replied.add(who)
            if cls in POSITIVE:
                positive.add(who)
            if t["meeting_booked_at"].strip():
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


def count(touches_path, change_path, today, read_date=None, baseline=None, candidate=None):
    out = {"touches": touches_path, "today": today.isoformat(), "problems": []}
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
    outbound = []
    for r in rows:
        if r["direction"].strip() != "outbound":
            out.setdefault("not_outbound_rows", []).append(r["touch_id"])
            continue
        if not day(r["sent_at"]) or not person(r):
            out["problems"].append(f"{r['touch_id']}: no valid sent_at or no person; not counted")
            continue
        outbound.append(r)
    if candidate:
        c_rows = [r for r in outbound if candidate[0] <= day(r["sent_at"]) <= candidate[1]]
        c_start, c_end = candidate
    else:
        c_rows = [r for r in outbound if change_id and r["change_id"].strip() == change_id]
        dates = sorted(day(r["sent_at"]) for r in c_rows)
        c_start, c_end = (dates[0], dates[-1]) if dates else (None, None)
    if baseline:
        b_start, b_end = baseline
        b_rows = [r for r in outbound if b_start <= day(r["sent_at"]) <= b_end]
    else:
        changed = day(rec.get("changed_at"))
        b_start = changed - datetime.timedelta(days=BASELINE_DAYS) if changed else None
        b_end = changed - datetime.timedelta(days=1) if changed else None
        channels = {r["channel"].strip() for r in c_rows}
        b_rows = [r for r in outbound if changed and not r["change_id"].strip()
                  and r["channel"].strip() in channels and b_start <= day(r["sent_at"]) <= b_end]
    out["windows"] = {"baseline": window_stats(b_rows, b_start, b_end),
                      "candidate": window_stats(c_rows, c_start, c_end)}
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
    out["days_since_last_candidate_send"] = (today - c_end).days if c_end else None
    first = day(out["windows"]["candidate"]["first_sent"])
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
        with open(touches, "w", encoding="utf-8") as f:
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
