---
name: contact-retention-review
description: "Use when existing CRM contacts need keep, restorable archive, hold, or duplicate-merge decisions. Applies contact protection and verified-move rules to ICP accounts, records evidence for every contact, and writes proposals for a person to approve."
license: MIT
---

# Contact retention review

Reviews existing contacts without deleting people. `brain/contact-rules.md` owns the team's retention policy.

## Evidence and gaps

**Protect** is the leading word. An open deal, recent activity, or Opportunity account protects a record before any archive rule runs. Every decision cites the contact ID, company ID, exact values, date of review, and rule IDs. Unknown company identity or missing rule inputs stay gaps.

## Inputs

- `brain/crm-export/companies.csv` and `contacts.csv`; optional `move-evidence.csv` for work-history proof. The synthetic `move-contacts.csv` sidecar belongs to the move-routing fixture, outside this review's `contacts.csv` scope.
- `brain/crm-export/README.md`, `brain/icp.md`, `brain/contact-rules.md`, and `brain/proposals/README.md`.

## Connect

Use the local CSV export for this wave, even if a live CRM connector is installed. Take an as-of review date; the example cases use 2026-09-28. Read optional `move-evidence.csv` only when it exists. The skill writes only a new local proposal file. A person approves and applies CRM changes.

## Source check

Before a step uses a fact or proposes a value or record, find the fact's row in "Where to look" in `brain/sources.md` and apply its Conflict order. Cite the winning source's rule ID and read date. A fact with no row is a gap (`source-unmapped`). A copy older than its "Fresh for" days, counted to the date of the run, is stale. Protection reads live status (open deal, activity, stage) from the export, a copy (`source-export-copy`). When company or contact rows disagree on a value that protection or ICP scope uses, with no winner, decide `hold`, propose no archive or merge for that contact, and list both values and the rule ID under Gaps for person. When the export is stale, decide `hold` for every contact whose decision depends on it, propose no archive or merge, and state the export's age under Gaps for person. Never pick one value silently, and keep this ranking in `brain/sources.md`, not here.

## Steps

1. **Scope and group.** Read every contact and its company. Apply `keep-scope` using checkable ICP conditions; leave clear non-ICP accounts out of scope. A criterion with no export column is an approval gap, not a failed condition. An explicit `unknown` or empty value in a checkable ICP column makes the account ambiguous; review its contacts conservatively and propose no archive until a person resolves fit. Group duplicate companies by domain for person matching. The step is done when every contact is in scope, out of scope, or at an ambiguous account, with the company values cited and missing-column gaps listed.
2. **Protect and match.** For each in-scope or ambiguous contact, test `keep-protected` using the review date: an open deal, activity within the preceding 12 months, or an Opportunity account. Compare LinkedIn URLs across the whole export, then name plus company domain when URLs are empty. For a duplicate, propose merging the weaker record into the protected or more active record; state which fields need human reconciliation. The step is done when every contact has a protection result and every duplicate group has one proposed survivor or an identity gap. Apply the source check to every value that protection reads.
3. **Verify departures and decide.** Compare `linkedin_current_company` with the company names in the contact's domain group, ignoring case and legal suffixes such as Inc. and LLC. Record a legal-suffix match as the same employer in the review. A name mismatch is a review flag. If `move-evidence.csv` exists, apply `move-verified` from `brain/contact-rules.md` with the review date to every reviewed contact with a linked evidence row, even when employer names match. Match both profile URL and person name; list evidence rows for contacts outside `contacts.csv` as outside this review. Preserve the origin role in the review. Missing evidence, conflicting current employers, concurrent roles, stale or future observations, date gaps, and other `move-verified` uncertainty cases remain possible moves for a person to check; propose no departure archive or company-field change from them. Apply this decision order: protected survivor `keep`; duplicate non-survivor `merge`; unverified email `hold-unverified`; confirmed move `archive` when unprotected; wrong function `archive-wrong-function` when unprotected; otherwise `keep`. Every archive cites `archive-restorable`; at an ambiguous ICP account, turn an archive into hold pending the ICP check. This skill creates no move owner task; `contact-move-routing` owns that action. The step is done when every reviewed contact has one primary decision and each name mismatch has a verified classification or a stated evidence gap.
4. **Write and stop.** Write one new `brain/proposals/<today>-contact-retention-review-<topic>.md` in the format below. Put archive and merge actions in proposal rows; keep, hold, and out-of-scope decisions in the review table. If the path exists, stop without overwriting. The run is done when every export contact ID appears in exactly one review decision and each action row cites its source values and rule ID.

## Write boundary

Write only a new file in `brain/proposals/`. Archives are restorable proposals. Keep `company_id` and confirmed fields unchanged. The export and CRM remain as read until a person applies approved actions.

## Proposal format

```markdown
---
skill: contact-retention-review
created_at: <YYYY-MM-DD>
status: proposed
approved_by:
source: <CRM name (read-only) or brain/crm-export/*.csv>
review_date: <YYYY-MM-DD>
---

| # | Object | Record ID | Field | Old value | New value | Reason | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | contact | <contact ID> | archive record | (blank) | restorable | <rule IDs> | <contact and company values> |

## Review decisions
| Contact | Company | Decision: keep, hold, archive, merge, or out of scope | Protection evidence | Rule IDs | Other evidence or gap |

## Possible and verified moves
| Contact | Origin role and domain | LinkedIn employer name | Evidence row and observed date or gap | `move-verified` result | Retention effect |

## Gaps for person
| Contact | Missing fact | Why it matters |
```
