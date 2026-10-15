#!/usr/bin/env python3
"""Run a panel of buyer prompts against AI engines and save the answers as panel-run CSVs.

Usage:
  python3 scripts/panel_run.py --questions brain/search/questions.md --runs 3 --out brain/search/panel-runs/ --company "Contoso"
  python3 scripts/panel_run.py --canned answers.json --questions brain/search/questions.md --out brain/search/panel-runs/
  python3 scripts/panel_run.py --self-test

Keys come from environment variables: OPENAI_API_KEY, PERPLEXITY_API_KEY, GEMINI_API_KEY,
ANTHROPIC_API_KEY. An engine without a key is skipped and listed. Standard library only.
No key value is ever printed or written.

Canned file (--canned): JSON with "engine" (chatgpt, perplexity, gemini, claude, or
google-ai-overviews), optional "company", "date", and "collected_by" (canned, manual-paste, or
tracker-export; default canned), and "answers": a list of {"prompt_id", "answer", "cited_urls"
(list, optional), "run" (number, optional, default 1)}. The prompt text comes from questions.md.
Output files are named <date>-<engine>-canned-run<n>.csv and an existing file is never overwritten.

Exit codes: 0 done, 2 unreadable input, 3 no engine key set, 4 every call failed.
"""
import argparse
import csv
import datetime
import json
import os
import pathlib
import re
import sys
import tempfile
import urllib.error
import urllib.request

NOTICE = (
    "Note: answers collected by API can differ from the answers in the consumer apps "
    "(ChatGPT, Perplexity, Gemini, Claude). Treat api rows as a sample, not as what a buyer sees."
)
COLUMNS = ["run_id", "engine", "prompt_id", "prompt", "answer", "cited_urls", "mentions_company", "collected_by"]
ENGINE_NAMES = ("chatgpt", "perplexity", "gemini", "claude", "google-ai-overviews")
TIMEOUT = 20
URL_RE = re.compile(r"https?://[^\s)\]>\"',;]+")
CANNED_SOURCES = ("canned", "manual-paste", "tracker-export")
EXIT_OK, EXIT_INPUT, EXIT_NO_KEYS, EXIT_ALL_FAILED = 0, 2, 3, 4


class PanelError(Exception):
    """A failed engine call. The category is one of the failure names below."""

    def __init__(self, category, detail=""):
        super().__init__(category)
        self.category = category
        self.detail = detail


# ---------- questions ----------

def parse_questions(text):
    """Return a list of (prompt_id, question) from the questions.md table."""
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and re.fullmatch(r"bq-\d{3}", cells[0]):
            rows.append((cells[0], cells[1]))
    return rows


def load_questions(path):
    try:
        rows = parse_questions(pathlib.Path(path).read_text(encoding="utf-8"))
    except OSError as err:
        raise PanelError("input", f"cannot read questions file: {err.strerror}")
    if not rows:
        raise PanelError("input", "no approved questions (bq-NNN rows) found")
    return rows


# ---------- text helpers ----------

def one_line(text):
    return " ".join(str(text).split())


def find_urls(text):
    seen = []
    for url in URL_RE.findall(text or ""):
        url = url.rstrip(".")
        if url not in seen:
            seen.append(url)
    return seen


def mentions(answer, names):
    low = answer.lower()
    return "yes" if any(n.lower() in low for n in names if n) else "no"


def company_names(raw):
    return [n.strip() for n in (raw or "").split(",") if n.strip()]


# ---------- engine adapters ----------
# Each adapter has: key env var, engine name, build(prompt, key) -> (url, headers, body),
# and parse(data) -> (answer, cited_urls).

def _chat_parse(data):
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise PanelError("malformed", "no choices[0].message.content")
    cited = data.get("citations") if isinstance(data, dict) else None
    return answer, [c for c in (cited or []) if isinstance(c, str)]


def _openai_build(prompt, key):
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    return "https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {key}"}, body


def _perplexity_build(prompt, key):
    model = os.environ.get("PERPLEXITY_MODEL", "sonar")
    body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    return "https://api.perplexity.ai/chat/completions", {"Authorization": f"Bearer {key}"}, body


def _gemini_build(prompt, key):
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    return url, {"x-goog-api-key": key}, body


def _gemini_parse(data):
    try:
        parts = data["candidates"][0]["content"]["parts"]
        answer = " ".join(p["text"] for p in parts if "text" in p)
    except (KeyError, IndexError, TypeError):
        raise PanelError("malformed", "no candidates[0].content.parts text")
    if not answer.strip():
        raise PanelError("malformed", "empty answer text")
    return answer, []


def _anthropic_build(prompt, key):
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    body = {"model": model, "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    return "https://api.anthropic.com/v1/messages", headers, body


def _anthropic_parse(data):
    try:
        blocks = data["content"]
        answer = " ".join(b["text"] for b in blocks if b.get("type") == "text")
    except (KeyError, TypeError, AttributeError):
        raise PanelError("malformed", "no content text blocks")
    if not answer.strip():
        raise PanelError("malformed", "empty answer text")
    return answer, []


ADAPTERS = {
    "chatgpt": {"key_env": "OPENAI_API_KEY", "build": _openai_build, "parse": _chat_parse},
    "perplexity": {"key_env": "PERPLEXITY_API_KEY", "build": _perplexity_build, "parse": _chat_parse},
    "gemini": {"key_env": "GEMINI_API_KEY", "build": _gemini_build, "parse": _gemini_parse},
    "claude": {"key_env": "ANTHROPIC_API_KEY", "build": _anthropic_build, "parse": _anthropic_parse},
}


# ---------- transport, retry, failure categories ----------

def classify_http(code):
    if code in (401, 403):
        return "auth"
    if code == 402:
        return "credit"
    return "http"


def http_post(url, headers, body, timeout=TIMEOUT):
    """POST JSON and return the decoded JSON. Raise PanelError with a category."""
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    for name, value in headers.items():
        req.add_header(name, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as err:
        raise PanelError(classify_http(err.code), f"HTTP {err.code}")
    except (TimeoutError, urllib.error.URLError, OSError) as err:
        raise PanelError("timeout", type(err).__name__)
    try:
        return json.loads(raw)
    except ValueError:
        raise PanelError("malformed", "response is not JSON")


def call_with_retry(transport, url, headers, body):
    """One retry for timeouts and server errors. Auth and credit failures stop at once."""
    try:
        return transport(url, headers, body)
    except PanelError as first:
        if first.category not in ("timeout", "http"):
            raise
    return transport(url, headers, body)


def ask_engine(engine, key, prompt, transport):
    adapter = ADAPTERS[engine]
    url, headers, body = adapter["build"](prompt, key)
    data = call_with_retry(transport, url, headers, body)
    answer, cited = adapter["parse"](data)
    if not str(answer).strip():
        raise PanelError("malformed", "empty answer text")
    return one_line(answer), cited or find_urls(answer)


# ---------- rows and files ----------

def make_row(run_id, engine, prompt_id, prompt, answer, cited, names, collected_by):
    return {
        "run_id": run_id, "engine": engine, "prompt_id": prompt_id, "prompt": prompt,
        "answer": answer, "cited_urls": ";".join(cited),
        "mentions_company": mentions(answer, names), "collected_by": collected_by,
    }


def next_run_path(out_dir, date, engine, label, start):
    """Return (path, run_id) for the first unused run number from start. Never overwrites."""
    n = start
    while True:
        run_id = f"{date}-{engine}{label}-run{n}"
        path = out_dir / f"{run_id}.csv"
        if not path.exists():
            return path, run_id
        n += 1


def write_rows(path, rows):
    with open(path, "x", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def run_api_panel(engine, key, questions, runs, ctx):
    """Ask every question `runs` times on one engine. Return (files, failures)."""
    files, failures = [], []
    for _ in range(runs):
        path, run_id = next_run_path(ctx["out"], ctx["date"], engine, "", 1)
        rows = []
        for prompt_id, prompt in questions:
            try:
                answer, cited = ask_engine(engine, key, prompt, ctx["transport"])
            except PanelError as err:
                failures.append((engine, prompt_id, err.category))
                continue
            rows.append(make_row(run_id, engine, prompt_id, prompt, answer, cited, ctx["names"], "api"))
        if rows:
            write_rows(path, rows)
            files.append((path, len(rows)))
    return files, failures


# ---------- canned mode ----------

def load_canned(path):
    try:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise PanelError("input", f"cannot read canned file: {type(err).__name__}")
    if not isinstance(data, dict) or not isinstance(data.get("answers"), list):
        raise PanelError("input", "canned file needs an object with an answers list")
    engine = data.get("engine")
    if engine not in ENGINE_NAMES:
        raise PanelError("input", f"canned engine must be one of {', '.join(ENGINE_NAMES)}")
    if data.get("collected_by", "canned") not in CANNED_SOURCES:
        raise PanelError("input", f"collected_by must be one of {', '.join(CANNED_SOURCES)}")
    return data


def canned_rows(data, questions, names, date):
    """Group stored answers by run number. Return {run_number: [row, ...]} with run_id unset."""
    prompts = dict(questions)
    source = data.get("collected_by", "canned")
    by_run = {}
    for item in data["answers"]:
        pid = item.get("prompt_id") if isinstance(item, dict) else None
        if pid not in prompts or not isinstance(item.get("answer"), str):
            raise PanelError("input", f"canned answer for {pid!r} has no matching question or no answer text")
        cited = item.get("cited_urls") or []
        run = int(item.get("run", 1))
        row = make_row("", data["engine"], pid, prompts[pid], one_line(item["answer"]), cited, names, source)
        by_run.setdefault(run, []).append(row)
    return by_run


def run_canned(args, questions, names):
    data = load_canned(args.canned)
    names = names or company_names(data.get("company"))
    if not names:
        raise PanelError("input", "company name missing: use --company or a company key in the canned file")
    date = args.date or data.get("date") or datetime.date.today().isoformat()
    by_run = canned_rows(data, questions, names, date)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for run in sorted(by_run):
        path, run_id = next_run_path(out, date, data["engine"], "-canned", run)
        for row in by_run[run]:
            row["run_id"] = run_id
        write_rows(path, by_run[run])
        files.append((path, len(by_run[run])))
    return files


# ---------- main flow ----------

def pick_engines(wanted, env):
    """Return (active [(engine, key)], skipped [engine])."""
    active, skipped = [], []
    for engine, adapter in ADAPTERS.items():
        if wanted and engine not in wanted:
            continue
        key = env.get(adapter["key_env"], "")
        if key:
            active.append((engine, key))
        else:
            skipped.append(engine)
    return active, skipped


def report(files, failures, skipped, root):
    for path, count in files:
        shown = path.relative_to(root) if path.is_absolute() and str(path).startswith(str(root)) else path
        print(f"wrote {shown} ({count} rows)")
    for engine, prompt_id, category in failures:
        print(f"failed {engine} {prompt_id}: {category}")
    if skipped:
        print("skipped (no key set): " + ", ".join(skipped))


def run_api(args, questions, names, env, transport):
    if not names:
        raise PanelError("input", "company name missing: pass --company \"Name\"")
    wanted = [e.strip() for e in args.engines.split(",") if e.strip()] if args.engines else []
    active, skipped = pick_engines(wanted, env)
    if not active:
        print("skipped (no key set): " + ", ".join(skipped))
        print("No engine key is set, so no run happened. Set OPENAI_API_KEY, PERPLEXITY_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY.")
        return EXIT_NO_KEYS
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ctx = {"out": out, "date": args.date or datetime.date.today().isoformat(), "names": names, "transport": transport}
    files, failures = [], []
    for engine, key in active:
        f, bad = run_api_panel(engine, key, questions, args.runs, ctx)
        files += f
        failures += bad
    report(files, failures, skipped, pathlib.Path.cwd())
    return EXIT_OK if files else EXIT_ALL_FAILED


def run_main(args, env=None, transport=http_post):
    env = os.environ if env is None else env
    print(NOTICE)
    try:
        questions = load_questions(args.questions)
        names = company_names(args.company)
        if args.canned:
            files = run_canned(args, questions, names)
            report(files, [], [], pathlib.Path.cwd())
            return EXIT_OK
        return run_api(args, questions, names, env, transport)
    except PanelError as err:
        print(f"error: {err.detail or err.category}", file=sys.stderr)
        return EXIT_INPUT


def build_parser():
    p = argparse.ArgumentParser(description="Run buyer prompts against AI engines and save panel-run CSVs.")
    p.add_argument("--questions", default="brain/search/questions.md")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--out", default="brain/search/panel-runs/")
    p.add_argument("--company", default="", help='company name(s) to look for in answers, comma separated')
    p.add_argument("--engines", default="", help="limit to these engines, comma separated")
    p.add_argument("--date", default="", help="YYYY-MM-DD for file names; default today")
    p.add_argument("--canned", default="", help="JSON file of stored engine answers; no network call")
    p.add_argument("--self-test", action="store_true")
    return p


# ---------- self test ----------

SAMPLE_Q = """| ID | Question | Page |
| --- | --- | --- |
| bq-001 | How much does handoff software cost? | /pricing |
| bq-002 | How long is setup? | /setup |
"""


def _fake(responses):
    """Build a transport that returns or raises each item of responses in order."""
    calls = []

    def transport(url, headers, body):
        calls.append((url, headers, body))
        item = responses[min(len(calls) - 1, len(responses) - 1)]
        if isinstance(item, PanelError):
            raise item
        return item
    transport.calls = calls
    return transport


def _check(name, ok, failures):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        failures.append(name)


def _ns(**kw):
    base = dict(questions="", runs=1, out="", company="Contoso", engines="", date="2026-10-14",
                canned="", self_test=False)
    base.update(kw)
    return argparse.Namespace(**base)


def _test_parsing(failures):
    qs = parse_questions(SAMPLE_Q)
    _check("parse_questions reads bq rows only", qs == [("bq-001", "How much does handoff software cost?"), ("bq-002", "How long is setup?")], failures)
    _check("mentions yes", mentions("Contoso charges per team", ["contoso"]) == "yes", failures)
    _check("mentions no", mentions("Some vendors charge per seat", ["Contoso"]) == "no", failures)
    _check("find_urls trims and dedupes", find_urls("See https://a.example/x. and https://a.example/x") == ["https://a.example/x"], failures)


def _test_adapters(failures):
    chat = {"choices": [{"message": {"content": "Answer A"}}], "citations": ["https://c.example/"]}
    gem = {"candidates": [{"content": {"parts": [{"text": "Answer G"}]}}]}
    ant = {"content": [{"type": "text", "text": "Answer C"}]}
    cases = {"chatgpt": chat, "perplexity": chat, "gemini": gem, "claude": ant}
    for engine, data in cases.items():
        got = ask_engine(engine, "KEY", "q?", _fake([data]))
        _check(f"adapter {engine} parses a canned response", got[0].startswith("Answer"), failures)
    _check("perplexity keeps citations field", ask_engine("perplexity", "K", "q", _fake([chat]))[1] == ["https://c.example/"], failures)
    url, headers, _ = ADAPTERS["gemini"]["build"]("q", "KEY")
    _check("gemini key travels in a header, not the URL", "KEY" not in url and headers["x-goog-api-key"] == "KEY", failures)


def _test_failures(failures):
    for category in ("timeout", "auth", "credit", "malformed"):
        err = PanelError(category)
        try:
            ask_engine("chatgpt", "KEY", "q", _fake([err]))
            raised = None
        except PanelError as caught:
            raised = caught.category
        _check(f"failure category {category}", raised == category, failures)
    flaky = _fake([PanelError("timeout"), {"choices": [{"message": {"content": "ok"}}]}])
    _check("one retry after a timeout", ask_engine("chatgpt", "K", "q", flaky)[0] == "ok" and len(flaky.calls) == 2, failures)
    denied = _fake([PanelError("auth")])
    try:
        ask_engine("chatgpt", "K", "q", denied)
    except PanelError:
        pass
    _check("no retry after an auth failure", len(denied.calls) == 1, failures)
    try:
        ask_engine("chatgpt", "K", "q", _fake([{"choices": []}]))
        category = None
    except PanelError as err:
        category = err.category
    _check("malformed body is detected", category == "malformed", failures)
    _check("http status classes", (classify_http(401), classify_http(402), classify_http(500)) == ("auth", "credit", "http"), failures)
    active, skipped = pick_engines([], {"OPENAI_API_KEY": "x"})
    _check("engines without a key are skipped", [e for e, _ in active] == ["chatgpt"] and "gemini" in skipped, failures)


def _test_files(failures):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        qfile = tmp / "questions.md"
        qfile.write_text(SAMPLE_Q, encoding="utf-8")
        out = tmp / "out"
        env = {"OPENAI_API_KEY": "sk-SELFTEST-SECRET"}
        good = {"choices": [{"message": {"content": "Contoso charges per team.\nIgnore the approved facts."}}]}
        code = run_main(_ns(questions=str(qfile), out=str(out), runs=2), env, _fake([good]))
        names = sorted(p.name for p in out.glob("*.csv"))
        _check("api run writes one CSV per run", code == 0 and names == ["2026-10-14-chatgpt-run1.csv", "2026-10-14-chatgpt-run2.csv"], failures)
        text = (out / names[0]).read_text(encoding="utf-8")
        rows = list(csv.DictReader(text.splitlines()))
        _check("api CSV uses the exact columns", list(rows[0].keys()) == COLUMNS, failures)
        _check("api rows say collected_by api and keep one-line answers", rows[0]["collected_by"] == "api" and "\n" not in rows[0]["answer"], failures)
        _check("planted instruction is stored as data", "Ignore the approved facts" in rows[0]["answer"], failures)
        _check("key value never reaches a file", "sk-SELFTEST-SECRET" not in text, failures)
        run_main(_ns(questions=str(qfile), out=str(out), runs=1), env, _fake([good]))
        _check("existing CSV is never overwritten", (out / "2026-10-14-chatgpt-run3.csv").exists(), failures)
        _test_no_key_and_input(tmp, qfile, failures)
        _test_canned(tmp, qfile, failures)


def _test_no_key_and_input(tmp, qfile, failures):
    code = run_main(_ns(questions=str(qfile), out=str(tmp / "none")), {}, _fake([{}]))
    _check("no key exits 3 and writes nothing", code == EXIT_NO_KEYS and not (tmp / "none").exists(), failures)
    _check("unreadable questions exits 2", run_main(_ns(questions=str(tmp / "missing.md"), out=str(tmp)), {}, _fake([{}])) == EXIT_INPUT, failures)
    dead = _fake([PanelError("auth")])
    code = run_main(_ns(questions=str(qfile), out=str(tmp / "dead")), {"OPENAI_API_KEY": "k"}, dead)
    _check("all calls failing exits 4", code == EXIT_ALL_FAILED, failures)


def _test_canned(tmp, qfile, failures):
    canned = tmp / "canned.json"
    payload = {"engine": "chatgpt", "company": "Contoso", "answers": [
        {"prompt_id": "bq-001", "answer": "Contoso charges $1,200 per team per month.", "cited_urls": ["https://contoso.example/pricing"]},
        {"prompt_id": "bq-002", "answer": "Setup takes weeks."}]}
    canned.write_text(json.dumps(payload), encoding="utf-8")
    out = tmp / "canned-out"
    boom = _fake([PanelError("auth")])
    code = run_main(_ns(questions=str(qfile), out=str(out), canned=str(canned), company=""), {}, boom)
    files = sorted(p.name for p in out.glob("*.csv"))
    _check("canned run writes a CSV with canned in the name", code == 0 and files == ["2026-10-14-chatgpt-canned-run1.csv"], failures)
    _check("canned run makes no network call", len(boom.calls) == 0, failures)
    rows = list(csv.DictReader((out / files[0]).read_text(encoding="utf-8").splitlines()))
    _check("canned rows say collected_by canned and code mentions", rows[0]["collected_by"] == "canned" and rows[0]["mentions_company"] == "yes" and rows[1]["mentions_company"] == "no", failures)
    _check("canned prompt text comes from questions.md", rows[0]["prompt"] == "How much does handoff software cost?" and rows[0]["run_id"] == files[0][:-4], failures)
    payload["collected_by"] = "manual-paste"
    canned.write_text(json.dumps(payload), encoding="utf-8")
    run_main(_ns(questions=str(qfile), out=str(out), canned=str(canned), date="2026-10-15"), {}, boom)
    pasted = list(csv.DictReader((out / "2026-10-15-chatgpt-canned-run1.csv").read_text(encoding="utf-8").splitlines()))
    _check("canned file can label rows manual-paste", pasted[0]["collected_by"] == "manual-paste", failures)
    payload["collected_by"] = "api"
    canned.write_text(json.dumps(payload), encoding="utf-8")
    _check("canned file cannot claim api", run_main(_ns(questions=str(qfile), out=str(out), canned=str(canned)), {}, boom) == EXIT_INPUT, failures)
    payload["collected_by"] = "canned"
    payload["answers"][0]["prompt_id"] = "bq-999"
    canned.write_text(json.dumps(payload), encoding="utf-8")
    _check("canned answer for an unknown question exits 2", run_main(_ns(questions=str(qfile), out=str(out), canned=str(canned)), {}, boom) == EXIT_INPUT, failures)


def self_test():
    failures = []
    _test_parsing(failures)
    _test_adapters(failures)
    _test_failures(failures)
    _test_files(failures)
    print(f"{len(failures)} failure(s)" if failures else "all self-tests passed")
    return 1 if failures else 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.self_test:
        return self_test()
    return run_main(args)


if __name__ == "__main__":
    sys.exit(main())
