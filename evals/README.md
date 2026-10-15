# Golden evals

Fixed cases with known answers. Each case runs a skill headless on a fresh copy of the repo and checks the files it writes. Run them after you change a brain file or a skill.

```bash
python3 evals/run.py                      # every case, 4 at a time, Sonnet 5.5
python3 evals/run.py sweep-budget --keep  # one case; keep its work folder and output
python3 evals/run.py --jobs 8 --model claude-haiku-4-5-20251001
```

Needs the `claude` CLI, signed in. Each case runs in its own copy under `~/.cache/gtm-brain-evals/`, so your `brain/` is never touched. A run costs one headless session per case.

## What the copy leaves out

Your own records never reach a case. Before the fixtures are copied in, the runner deletes from the copy:

- every file under `brain/search/` except the four rule files (`README.md`, `question-rules.md`, `writing-rules.md`, `banned-phrases.txt`), including `brain/search/panel-runs/`;
- every file under `brain/themes/`;
- `brain/calls/*.csv` and `brain/crm-export/*.csv`;
- `brain/voice.md` and `brain/proof.md`;
- the accounts, signals, and decisions in `brain/`.

`evals/fixtures/base/` then restores the invented Contoso and Northwind versions, including byte-identical copies of `brain/voice.md` and `brain/proof.md`. If you change either committed file, copy it to `evals/fixtures/base/brain/` too.

Check this with the sentinel test, which needs no `claude` session:

```bash
python3 evals/run.py --sentinel
```

It adds the marker `PRIVATE-SENTINEL` to `brain/search/panel-runs/`, `brain/themes/`, `brain/calls/call-notes.csv`, `brain/crm-export/contacts.csv`, `brain/voice.md`, and `brain/proof.md`, builds an eval copy, and fails if the marker appears in any file name or file in that copy. It then puts every planted file back exactly, so `git status` stays clean.

## Tools a case may use

A case session may read and write files, and it may run two commands only: `python3 scripts/content_checks.py` and `python3 scripts/panel_run.py --canned`. The canned mode reads stored answers from a file in the case and makes no network call. If `TYPESAFE_API_KEY` is set in your shell, `content_checks.py` can call Jev; with no key, every judgment field reads `judged_by: agent`.

## What a case checks

- The new decision files: how many, every one at `status: proposed` with `approved_by` and `verdict_date` empty, and for each account and signal the `decision`, `rule`, `play`, and text that must or must not appear under Gaps.
- What the run shows the person: patterns that must or must not appear, and `output_order` pairs where the first must come before the second.
- Each decision file names the expected signal, is named `<today>-<account>-<signal>.md`, and has `decided_at` set to the case date. `no_draft` asserts the draft is `none`.
- That nothing outside new files in `brain/decisions/` changed. A verdict case may change only the verdict fields of named decisions (`verdict_files`: `status`, `verdict_reason`, `approved_by`, `verdict_date`) and append to named files (`append_only`), and checks their text with `file_has`.

## Cases

| Case | What it proves |
| --- | --- |
| `handoff-northwind` | The walkthrough account gets `act-now`, `rule-act-now`, play `first-gtm-hire` |
| `handoff-no-recipient-or-owner` | `act-now` with no valid email and no owner stays `act-now`, with the gaps "no recipient" and "no owner" |
| `handoff-route-no-owner` | An Opportunity account with a blank owner is still `route-to-owner` with no draft, and the gap "no owner" |
| `handoff-skip-icp-fail` | A consumer company is skipped (`rule-skip`) |
| `handoff-route-to-owner` | An account at Opportunity goes to its owner, with no draft |
| `handoff-relative-whynow` | A `whyNow` with no calendar date blocks `act-now` |
| `handoff-missing-verdict` | No `relevanceVerdict` means `nurture`, with the gap listed |
| `handoff-stage-conflict-unresolved` | Two stage copies read the same day: neither wins, so no stage rule matches |
| `handoff-stage-later-copy` | The copy read later wins (`source-export-copy`) |
| `handoff-budget-full` | 5 `act-now` this week: `nurture` with the gap "handoff budget full" |
| `handoff-budget-rejected-frees` | A rejected `act-now` frees its slot |
| `handoff-budget-old-window` | `act-now` decisions older than 7 days do not count |
| `sweep-budget` | Seven signals, budget 2: the two strongest get `act-now`, the rest decided in order |
| `sweep-held-first` | Next day: a held account takes a freed slot ahead of a stronger new signal |
| `sweep-quiet` | Every signal decided: "No handoffs today." |
| `sweep-stale` | Newest signal 10 days old: the stale-feed warning comes before the first handoff |
| `sweep-empty-feed` | No signals at all: the empty-feed warning comes before any "No handoffs today." |
| `sweep-blocked-input` | A decision blocked by a missing input is shown, not only counted |
| `verdict-correction-format` | A rejection sets `status: rejected` and adds a corrections line with the decision path and `applies when` |
| `verdict-records-approver` | An approval by a named person sets `approved_by` and `verdict_date`, changes no other line, and adds no corrections line |
| `handoff-supersedes-held` | A new decision on a signal held the day before names the held file in `supersedes` and leaves it unedited |
| `correction-no-false-promotion` | Three lines on one ID with different conditions or one-off scope propose no rule edit |
| `correction-promotes-on-three` | Three lines on one ID and one condition from three accounts: the skill proposes an edit, starting `Proposed rule edit: rule-act-now` |
| `correction-same-account-no-promotion` | Three matching lines from one account: no edit is proposed |
| `correction-different-conditions-no-promotion` | Three accounts and one ID, but two different conditions: no edit is proposed |
| `rule-edit-approved` | A named person approves the exact proposed edit to `rule-act-now`: `brain/stages.md` changes by that one edit, and no decision, correction, or other file changes |
| `sources-conflict-tiered-contact-build` | Two company rows at one domain, read the same day, give different revenue: the account is escalated with both values and no tier (`source-export-copy`) |
| `sources-stale-export-retention` | An export read 48 days before the review is stale: no archive or merge rows, and the age is reported |
| `icp-calibration-stale-export` | Calibration 48 days after the export: every company value is stale, so no record matches, the age is reported, and the verdict asks for a fresher export instead of tighten or loosen |
| `themes-stale-export` | Call themes 48 days after the export: the theme is `none` although two domains would otherwise qualify, Facts still list the confirmed quotes, and Gaps state the export age |
| `setup-fresh-days` | A sources.md redo with a new freshness number (14 days) for the two CRM rows: the proposal carries 14 and today's check date on those rows, keeps the other numbers, leaves `brain/sources.md` unchanged, and stays proposed |
| `objections-to-questions-contoso` | Contoso call notes and themes turn objections into the questions a buyer would type, in one proposal under `brain/search/proposals/` |
| `cited-brief-checks` | A draft with one phrase used five times, two banned phrases, and one sentence over 25 words: the check JSON under `brain/search/checks/` exists and names all of them |
| `buyer-prompt-panel-canned` | `panel_run.py --canned` on stored engine answers writes a CSV under `brain/search/panel-runs/` with the right `collected_by`, and makes no network call |
| `mention-to-deal-ledger-month` | One month of mentions and deals: the AI-or-search deal set and the unknown deal set match the answer key |
| `brand-facts-audit-injection` | An answer that carries an instruction is reported as an instruction, not followed; the planted mismatches are reported and `brain/search/brand-facts.md` is unchanged |
| `competitor-comparison-pages-relaymark` | A comparison page plan for the Relaymark competitor card, written as one proposal |
| `start-here-clear` | One request whose skill the descriptions fix: the routing answer names that skill, never `none` or another skill |
| `start-here-unsupported` | An outbound-send request that no skill covers: the routing answer is `none` |
| `brand-facts-audit-accurate` | An answer that matches `brain/search/brand-facts.md` raises no finding |

## Add a case

Make `evals/cases/<id>/case.json`:

```json
{
  "request": "Run account-handoff for Northwind Robotics on the 2026-09-24 signal.",
  "today": "2026-10-03",
  "fixtures": [],
  "replace": [{"file": "brain/stages.md", "old": "at most 5", "new": "at most 2"}],
  "delete": [],
  "expect": {
    "decision_count": 1,
    "decisions": [{"account": "northwind-robotics", "signal": "brain/signals/2026-09-24-northwind-founding-gtm-engineer.md", "decision": "act-now", "gaps": [], "no_gaps": []}],
    "output_has": [],
    "output_lacks": []
  }
}
```

Every case starts from `evals/fixtures/base/` (the Northwind account, signal, and CRM export) with your accounts, signals, and decisions removed, so only your rules and skills are under test. Files under `evals/cases/<id>/files/` and each named folder in `evals/fixtures/` are copied over the repo copy before the run. Each `replace` text must appear exactly once. Each `append` entry (`{"file": ..., "text": ...}`) adds its text to the end of that file, so a case can seed history without replacing the file's own rules. Two optional keys serve cases that record a verdict instead of writing a decision:

- `"verdict_files": ["brain/decisions/<file>"]` lets those decision files change their `status`, `verdict_reason`, `approved_by`, and `verdict_date` lines only. The fixture must already carry those lines, empty. Any other edit fails.
- `"append_only": ["brain/corrections.md"]` lets those files gain lines at the end. Editing or removing an earlier line fails. A case without these keys behaves as before.
- `"new_files": ["brain/proposals/"]` lets the run create new files under those folders, for skills that write a proposal instead of a decision. New files anywhere else still fail. Each new file there must stay `status: proposed` with `approved_by` empty. `"new_file_has": {"brain/proposals/": ["regex", ...]}` requires a new file in that folder and each regex to match it; `"new_file_lacks"` fails on any match, such as a forbidden action row.
- `"edited_files": {"brain/stages.md": {"old": "...", "new": "..."}}` lets that file change by one exact replacement, for a case where a person approves a rule edit. `old` must appear once in the file before the run, and the file after the run must equal the file before with `old` replaced by `new`. Any other change, a missing edit, or a repeated edit fails.
- `"no_status_files": ["brain/calibration/"]` exempts new files under those paths from the `status: proposed` requirement, for a record format with no status field (a calibration record or a rebuilt filter). They must still have `approved_by` empty. List the same paths in `new_files`.
- Content skills write under `brain/search/`. List `brain/search/proposals/` in `new_files`: each new file there must stay `status: proposed`. Machine outputs (`brain/search/checks/` and `brain/search/panel-runs/`) carry no status, so list them in both `new_files` and `no_status_files`; they must still have `approved_by` empty.
- `"file_has": {"brain/corrections.md": ["regex", ...]}` requires each regex to match in that file after the run (case-insensitive; `^` and `$` match at line breaks).

Write the expected answer from the rules before you run the case, never from the run's output.
