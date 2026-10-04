# Golden evals

Fixed cases with known answers. Each case runs a skill headless on a fresh copy of the repo and checks the files it writes. Run them after you change a brain file or a skill.

```bash
python3 evals/run.py                      # every case, 4 at a time, Sonnet 5.5
python3 evals/run.py sweep-budget --keep  # one case; keep its work folder and output
python3 evals/run.py --jobs 8 --model claude-haiku-4-5-20251001
```

Needs the `claude` CLI, signed in. Each case runs in its own copy under `~/.cache/gtm-brain-evals/`, so your `brain/` is never touched. A run costs one headless session per case.

## What a case checks

- The new decision files: how many, every one at `status: proposed` with `approved_by` and `verdict_date` empty, and for each account and signal the `decision`, `rule`, `play`, and text that must or must not appear under Gaps.
- What the run shows the person: patterns that must or must not appear, and `output_order` pairs where the first must come before the second.
- Each decision file names the expected signal, is named `<today>-<account>-<signal>.md`, and has `decided_at` set to the case date. `no_draft` asserts the draft is `none`.
- That nothing outside new files in `brain/decisions/` changed. A verdict case may change only the verdict fields of named decisions (`verdict_files`: `status`, `verdict_reason`, `approved_by`, `verdict_date`) and append to named files (`append_only`), and checks their text with `file_has`.

## Cases

| Case | What it proves |
| --- | --- |
| `handoff-northwind` | The walkthrough account gets `act-now`, `rule-act-now`, play `first-gtm-hire` |
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
- `"file_has": {"brain/corrections.md": ["regex", ...]}` requires each regex to match in that file after the run (case-insensitive; `^` and `$` match at line breaks).

Write the expected answer from the rules before you run the case, never from the run's output.
