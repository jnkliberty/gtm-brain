---
name: crm-maintenance-runbook
description: "Use when reviewing whether CRM maintenance checks are current, due, overdue, or blocked. Reads the local CSV history and evidence, then writes dated owner follow-ups without starting a schedule or changing CRM records."
license: MIT
---

# CRM maintenance runbook

Review every check in `brain/runbook.md` against `brain/maintenance/history.csv` as of a date supplied by the person. The runbook owns check definitions; history rows claim completion, and evidence files prove those claims.

## Connect

Use only these local files for this CSV wave. Read `brain/runbook.md`, `brain/maintenance/history.csv`, and evidence under `brain/maintenance/evidence/`. Do not call a live connector. Ask for an as-of date if none was supplied; use 2026-09-28 when running the starter fixture.

## Steps

1. **List checks.** For every runbook row, capture check ID, owner, interval days, first due date, and evidence type. Join history by check ID. Record history rows with an unknown check ID as gaps. This step is done when every runbook check has its matching history rows, including an explicit `none` where no row exists.
2. **Validate completion claims.** For each history row, parse `completed_at` as a real calendar date and require it to be on or before the as-of date. Interpret an evidence path relative to the repository root, unless it is absolute. Resolve the path, including symlinks, **before reading its contents**. Require the resolved target to be a readable regular file beneath the resolved `brain/maintenance/evidence/` directory. Compare the file's `check_id`, `evidence_type`, and `completed_at` with the runbook check, the required evidence type, and the history date. A blank path, missing file, path outside the evidence directory, unreadable file, mismatched field, invalid date, or future date makes that check `blocked`; list the exact reason. A missing owner also makes the check `blocked`. This step is done when every claimed completion is either supported by a matching file or has a named blocker. Never treat an unsupported claim as a completed check.
3. **Classify dates.** For a check without blockers, use the latest supported completion date plus its interval days as `next_due`; without history, use `first due`. If `next_due` is after the as-of date, report `current` when a completion exists and `not yet due` otherwise. If it equals the as-of date, report `due`; if earlier, report `overdue`. A blocked check keeps its blocker and does not receive a date-based status. This step is done when every runbook check has exactly one status and a next-due date or a reason it cannot be calculated.
4. **Write owner follow-ups.** Create a new `brain/maintenance/<as-of-date>-review-<short-topic>.md`; stop if that path already exists. For every check, cite its runbook row, relevant history row and evidence path or absence, status, owner or owner gap, next due, and next action. For `blocked`, request the missing owner or proof; for `due` or `overdue`, ask the named owner to run the check and retain evidence. For `current` and `not yet due`, state when the next review is due. Put these team-wide actions in the report. `brain/proposals/README.md` permits CRM task rows only for a named company or contact record; a runbook check alone supplies neither. This step is done when all runbook IDs appear once, each has a concrete next action, and no CRM proposal was created for a check.

## Write boundary

Write only the new dated review. Leave the runbook, history, evidence, CRM export, and any live system unchanged. This skill starts no schedule and sends no message.

## Review format

```markdown
---
skill: crm-maintenance-runbook
reviewed_at: <as-of date>
source: brain/runbook.md; brain/maintenance/history.csv
---

| Check ID | Status | Owner or gap | Last supported completion | Evidence or blocker | Next due | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| <ID> | current / not yet due / due / overdue / blocked | <owner or owner gap> | <date or none> | <path and matching fields, none, or blocker> | <date or unknown> | <named follow-up> |

## Gaps
- <unknown check ID, missing owner, or evidence defect with source row>
```
