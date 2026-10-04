#!/usr/bin/env python3
"""Run the golden eval cases headless and check each result on disk.

Usage: python3 evals/run.py [case ...] [--model M] [--jobs N] [--keep]
"""
import argparse
import concurrent.futures
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
CASES = REPO / "evals" / "cases"
FIXTURES = REPO / "evals" / "fixtures"
TOOLS = "Read,Glob,Grep,LS,Write,Edit"
# Claude Code refuses writes inside the loaded plugin and under the system temp folder,
# so the plugin loads from the repo and each case writes to its own copy here.
RUNS = pathlib.Path.home() / ".cache" / "gtm-brain-evals"


def prepare(case, work):
    shutil.copytree(REPO, work, ignore=shutil.ignore_patterns(".git", ".worktrees", "evals", "tests"))
    # Records come from fixed fixtures; only the rules and skills are yours. Your own
    # accounts, signals, decisions, and export would change what each case decides.
    for folder in ("accounts", "signals", "decisions"):
        for old in (work / "brain" / folder).glob("*.md"):
            old.unlink()
    for name in ["base"] + case.get("fixtures", []):
        shutil.copytree(FIXTURES / name, work, dirs_exist_ok=True)
    own = CASES / case["id"] / "files"
    if own.is_dir():
        shutil.copytree(own, work, dirs_exist_ok=True)
    for a in case.get("append", []):
        target = work / a["file"]
        text = target.read_text()
        target.write_text(text + ("" if text.endswith("\n") else "\n") + a["text"])
    for rel in case.get("delete", []):
        (work / rel).unlink()
    for r in case.get("replace", []):
        p = work / r["file"]
        text = p.read_text()
        if text.count(r["old"]) != 1:
            raise ValueError(f"{case['id']}: replace text must appear once in {r['file']}")
        p.write_text(text.replace(r["old"], r["new"]))


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def field(text, key):
    m = re.search(rf"^{key}:[ \t]*(.*)$", text, re.M)
    return m.group(1).strip() if m else None


def appended(old, new):
    prefix = old if not old or old.endswith(b"\n") else old + b"\n"
    return new == old or new.startswith(prefix)


def strip_verdict(data):
    # Blank only the verdict values in the frontmatter; the body must match exactly.
    m = re.match(rb"(---\n.*?\n---\n)(.*)", data, re.S)
    if not m:
        return data
    head = re.sub(rb"(?m)^(status|verdict_reason|approved_by|verdict_date):.*$", rb"\1:", m.group(1))
    return head + m.group(2)


def section(text, name):
    m = re.search(rf"^## {name}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def check(case, before, after, output):
    exp, fails = case["expect"], []
    new = {k: v.decode() for k, v in after.items() if k not in before and k.startswith("brain/decisions/")}
    changed = [k for k in after if k in before and after[k] != before[k]]
    stray = [k for k in after if k not in before
             and not k.startswith(("brain/decisions/", *exp.get("new_files", [])))]
    gone = [k for k in before if k not in after]
    # A verdict may change only the verdict fields of its decision and append to listed files.
    verdict_ok = {k for k in exp.get("verdict_files", []) if k in before and k in after
                  and strip_verdict(before[k]) == strip_verdict(after[k])}
    append_ok = {k for k in exp.get("append_only", []) if k in before and k in after
                 and appended(before[k], after[k])}
    # An edited file must equal its before text with the one listed replacement, and nothing else.
    edited_ok = set()
    for k, e in exp.get("edited_files", {}).items():
        old, rep = before.get(k, b"").decode(), after.get(k, b"").decode()
        if old.count(e["old"]) == 1 and rep == old.replace(e["old"], e["new"]):
            edited_ok.add(k)
        else:
            fails.append(f"{k}: not changed by exactly the one approved edit")
    changed = [k for k in changed if k not in verdict_ok | append_ok | edited_ok]
    if changed or stray or gone:
        fails.append(f"files outside new decisions touched: {sorted(changed + stray + gone)}")
    for k, t in new.items():
        if field(t, "status") != "proposed":
            fails.append(f"{k}: status is {field(t, 'status')!r}; only a person approves")
        for key in ("approved_by", "verdict_date"):
            if field(t, key):
                fails.append(f"{k}: {key} is set on a new decision; only a verdict sets it")
    if "decision_count" in exp and len(new) != exp["decision_count"]:
        fails.append(f"expected {exp['decision_count']} new decision files, got {len(new)}: {sorted(new)}")
    for want in exp.get("decisions", []):
        hits = [(k, t) for k, t in new.items()
                if field(t, "account") == want["account"] and field(t, "signal") == want["signal"]]
        if len(hits) != 1:
            fails.append(f"{want['account']}: expected 1 new decision file for {want['signal']}, got {len(hits)}")
            continue
        name, t = hits[0]
        sig = want["signal"]
        if name != f"brain/decisions/{case['today']}-{want['account']}-{pathlib.Path(sig).stem}.md":
            fails.append(f"{want['account']}: file name {name} does not match today, account, and signal")
        if field(t, "decided_at") != case["today"]:
            fails.append(f"{want['account']}: decided_at is {field(t, 'decided_at')!r}, expected {case['today']!r}")
        if want.get("no_draft"):
            draft = section(t, r"Draft \(DRAFT, not sent\)").split("Draft evidence")[0]
            if [line.strip() for line in draft.splitlines() if line.strip()] != ["To: none", "none"]:
                fails.append(f"{want['account']}: wrote a draft")
        for key in ("decision", "rule", "play"):
            if key in want and field(t, key) != want[key]:
                fails.append(f"{want['account']}: {key} is {field(t, key)!r}, expected {want[key]!r}")
        gaps = section(t, "Gaps").lower()
        for g in want.get("gaps", []):
            if g.lower() not in gaps:
                fails.append(f"{want['account']}: Gaps lacks {g!r}")
        for g in want.get("no_gaps", []):
            if g.lower() in gaps:
                fails.append(f"{want['account']}: Gaps has {g!r}")
    # New files in `new_files` folders are proposals too: still proposed, approved by no one.
    made = {k: v.decode() for k, v in after.items() if k not in before
            and exp.get("new_files") and k.startswith(tuple(exp["new_files"]))}
    for k, t in made.items():
        if field(t, "status") != "proposed" or field(t, "approved_by"):
            fails.append(f"{k}: not left proposed and unapproved; only a person approves")
    for folder, pats in exp.get("new_file_has", {}).items():
        text = "\n".join(t for k, t in made.items() if k.startswith(folder))
        if not text:
            fails.append(f"no new file under {folder}")
        for pat in pats:
            if text and not re.search(pat, text, re.I | re.M):
                fails.append(f"new file under {folder} lacks /{pat}/")
    for folder, pats in exp.get("new_file_lacks", {}).items():
        text = "\n".join(t for k, t in made.items() if k.startswith(folder))
        for pat in pats:
            if re.search(pat, text, re.I | re.M):
                fails.append(f"new file under {folder} has /{pat}/")
    for path, pats in exp.get("file_has", {}).items():
        text = after.get(path, b"").decode()
        for pat in pats:
            if not re.search(pat, text, re.I | re.M):
                fails.append(f"{path} lacks /{pat}/")
    for pat in exp.get("output_has", []):
        if not re.search(pat, output, re.I | re.S):
            fails.append(f"output lacks /{pat}/")
    for first, then in exp.get("output_order", []):
        a = re.search(first, output, re.I | re.S)
        b = re.search(then, output, re.I | re.S)
        if not a or (b and b.start() < a.start()):
            fails.append(f"output does not show /{first}/ before /{then}/")
    for pat in exp.get("output_lacks", []):
        if re.search(pat, output, re.I | re.S):
            fails.append(f"output has /{pat}/")
    return fails


def run(case, model, keep):
    RUNS.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix=f"{case['id']}-", dir=RUNS))
    work = tmp / "repo"
    try:
        prepare(case, work)
        before = snapshot(work)
        prompt = (f"{case['request']} Today's date is {case['today']}. Work only in the current folder. "
                  "Follow the skill exactly and write only what it allows. Your final message is exactly what you would "
                  "show the person, with nothing added.")
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", model, "--plugin-dir", str(REPO),
             "--allowedTools", TOOLS, "--permission-mode", "acceptEdits",
             "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence"],
            cwd=work, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=case.get("timeout", 900))
        (tmp / "output.txt").write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr)
        if proc.returncode != 0:
            return case["id"], [f"claude exited {proc.returncode}: {proc.stderr.strip()[-300:]}"], tmp
        return case["id"], check(case, before, snapshot(work), proc.stdout), tmp
    except Exception as e:  # a crashed case is a failed case, not a crashed run
        return case["id"], [f"{type(e).__name__}: {e}"], tmp
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="*")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--keep", action="store_true", help="keep each case's work folder for inspection")
    a = ap.parse_args()
    cases = [json.loads(p.read_text()) | {"id": p.parent.name} for p in sorted(CASES.glob("*/case.json"))]
    unknown = set(a.cases) - {c["id"] for c in cases}
    if unknown:
        sys.exit(f"unknown case: {', '.join(sorted(unknown))}")
    if a.cases:
        cases = [c for c in cases if c["id"] in a.cases]
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as pool:
        results = list(pool.map(lambda c: run(c, a.model, a.keep), cases))
    failed = 0
    for cid, fails, tmp in results:
        print(f"{'PASS' if not fails else 'FAIL'}  {cid}" + (f"  ({tmp})" if a.keep else ""))
        for f in fails:
            print(f"      - {f}")
        failed += bool(fails)
    print(f"\n{len(results) - failed} of {len(results)} passed with {a.model}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
