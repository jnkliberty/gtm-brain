# CRM maintenance runbook (example)

Every check is local practice for this invented starter brain. The owner reviews evidence and decides the follow-up. This file starts no schedule.

| Check ID | Check | Owner | Interval days | First due | Evidence type |
| --- | --- | --- | ---: | --- | --- |
| M-CURRENT | Reconcile the sample account count | ops.owner | 30 | 2026-09-01 | review-note |
| M-UPCOMING | Review contact coverage | ops.owner | 30 | 2026-10-05 | review-note |
| M-DUE | Review field provenance | ops.owner | 30 | 2026-09-28 | review-note |
| M-OVERDUE | Review duplicate records | ops.owner | 30 | 2026-09-20 | review-note |
| M-MISSING | Confirm evidence was retained | ops.owner | 30 | 2026-09-01 | review-note |
| M-INVALID | Verify date entry | ops.owner | 30 | 2026-09-01 | review-note |
| M-FUTURE | Verify future entry | ops.owner | 30 | 2026-09-01 | review-note |
| M-ABSOLUTE | Verify absolute evidence path | ops.owner | 30 | 2026-09-01 | review-note |
| M-TRAVERSAL | Verify parent path | ops.owner | 30 | 2026-09-01 | review-note |
| M-SYMLINK | Verify linked evidence path | ops.owner | 30 | 2026-09-01 | review-note |
| M-WRONG-CHECK | Verify check identity | ops.owner | 30 | 2026-09-01 | review-note |
| M-WRONG-TYPE | Verify evidence type | ops.owner | 30 | 2026-09-01 | review-note |
| M-NO-OWNER | Assign the team-wide audit owner |  | 30 | 2026-09-20 | review-note |

## Evidence contract

`brain/maintenance/history.csv` records claimed completions. Each evidence file for a claimed completion contains `check_id`, `evidence_type`, and `completed_at` matching its runbook and history row. Resolve the evidence path before reading it. Only a readable file whose resolved path is under `brain/maintenance/evidence/` can support completion. A missing history row has no completion claim; classify it from its first due date. A missing owner or invalid completion claim is `blocked` before any due-date result. Put team-wide follow-ups in the dated maintenance review, with the named owner or an owner gap. A CRM proposal task needs a named company or contact record.
