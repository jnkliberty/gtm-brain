---
name: contact-move-routing
description: "Use when CSV work-history evidence may show a contact's job change. Classifies verified same-role, changed-role, and employer-move cases; groups duplicate people; routes one proposed follow-up to the CRM company's owner."
license: MIT
---

# Contact move routing

Classify work-history evidence as of a supplied date. `brain/contact-rules.md` owns `move-verified`; this skill owns move-field and owner-task proposals. A name mismatch in `linkedin_current_company` is a review flag, not move proof. Retention owns keep, hold, and archive decisions.

## Evidence and gaps

**Verify** identity, origin, dates, and destination before assigning a non-uncertain label. Cite the evidence `case_id`, contact IDs, company ID and domain, original and destination role, observation date, and `move-verified` in every decision. Record missing or conflicting facts as `uncertain` with the exact gap. Preserve the prior employer and role in the report.

## Inputs

- As-of date and a short output topic.
- `brain/crm-export/companies.csv`, `contacts.csv`, and `move-evidence.csv`. For the invented starter fixture, include `move-contacts.csv` as an overlay of two additional contact IDs. Ignore that synthetic sidecar for a real export unless the person explicitly names it.
- `brain/contact-rules.md`, `brain/field-rules.md`, and `brain/proposals/README.md`.
- Existing `brain/proposals/*.md` to check for proposed or approved owner tasks for the same move event.

## Connect

For this CSV wave, read the local files above. Do not call a live CRM or enrichment connector. Write only new local reports and proposals; a person approves and applies any CRM action.

## Source check

Before a step uses a fact or proposes a value or record, find the fact's row in "Where to look" in `brain/sources.md` and apply its Conflict order. Cite the winning source's rule ID and read date. A fact with no row is a gap (`source-unmapped`). A copy older than its "Fresh for" days, counted to the date of the run, is stale. The company owner and company domain come from the export, a copy (`source-export-copy`). Work-history evidence keeps its own limit: `move-verified` in `brain/contact-rules.md` still rejects an observation older than 90 days. When company rows for one company disagree on the owner with no winner, or the export is stale, record an owner gap, propose no task, and list both values and the rule ID under Gaps for person. Never pick one value silently, and keep this ranking in `brain/sources.md`, not here.

## Steps

1. **Join and group.** Join every selected contact, including the starter overlay when used, to `companies.csv` by `company_id`. Normalize profile URLs by lowercasing, removing a leading scheme and `www.`, and removing a trailing slash; normalize names by trimming and case-folding. Group rows only when both normalized profile URL and person name match. A URL shared by conflicting names is an identity gap for all affected rows. Match evidence by verified profile URL and person name; use `contact_id` to trace its source row, not to split a verified person. An evidence row linked by contact ID or profile URL whose name conflicts with the contact is `uncertain: identity`, not missing evidence. A contact with no linked evidence row gets `no move evidence`, no move label, and no action. This step is done when every source contact is assigned to one verified person group or an identity/evidence gap.
2. **Classify once per person.** First apply every uncertainty guard in `move-verified`: unmatched identity; missing or invalid `observed_at` or destination start date; any supplied role date after the as-of date; observation after the as-of date or older than 90 days; origin domain different from the contact's CRM company domain; active or overlapping roles at different-domain employers; conflicting recent current employers; or a destination title containing `advisor`, `fractional`, or `consultant`, ignoring case. A name-only origin match does not replace a domain match. A supplied origin end date must be a valid date. If the guards pass, label `same role` when verified origin and destination domains and titles match; `changed role` when the domain matches but the title differs and the destination role has a dated start; or `confirmed move` when the origin work-history role ended on a valid date and the active destination role has a different verified domain and dated start. A blank origin end date can support `same role` or `changed role` at the same domain, but leaves a different-domain case uncertain. Keep competing evidence rows together; do not select the most convenient row. This step is done when each verified person has one label with its supporting row IDs, or `uncertain` with the failed guard.
3. **Identify the event and route.** For `changed role` and `confirmed move`, form the event key `person key | origin domain | destination domain | destination start date`. The person key is the normalized profile URL; domains are lowercased and trimmed. For a same-company role change, use the company domain on both sides. Find the company's `owner` from its `company_id`, even when a contact row names another owner. If it is blank, record an owner gap. Before proposing a task, read **only** `task for owner` rows in `brain/proposals/*.md` whose file status is `proposed` or `approved`; unescape Markdown `\|` cell separators before comparing their event keys. A row with the same event key suppresses another task even when topic or observation date differs. `brain/moves/` reports do not establish task status. This step is done when every verified change has one event key, the source company owner or owner gap, and an explicit new-task or suppressed-task decision. Apply the source check to the owner and company values before proposing a task.
4. **Write and stop.** Create `brain/moves/<YYYY-MM-DD>-routing-<topic>.md` in the format below. Create `brain/proposals/<YYYY-MM-DD>-contact-move-routing-<topic>.md` only when there is a grounded company/contact action. Use `brain/proposals/README.md` row syntax, current export values as `Old value`, and the event key in the task row's `Reason`. A proposed `task for owner` targets the existing company record and names its company owner and requested review. For a `changed role` at the same company, propose the verified new title for each contact ID in that person group, using each contact's current title as its own old value. For a `confirmed move`, propose no destination title on the origin company's contact record; keep the destination role in the report for a person's reassociation decision. Treat a confirmed field without a safe mapping as a person-facing gap under `brain/field-rules.md`. Preserve the origin company association and ask the owner to review any reassociation; never blank or rewrite `company_id` from move evidence alone. If either output path already exists, choose a new topic or stop; never overwrite it. This step is done when every source person appears once in the report, every proposed row cites its evidence and event key where applicable, and no duplicate owner task was created.

## Write boundary

The export and CRM remain unchanged. No outreach, live write, or archive occurs. A proposal is a request for human approval, including when evidence confirms a move.

## Move report format

```markdown
---
skill: contact-move-routing
created_at: <YYYY-MM-DD>
as_of: <YYYY-MM-DD>
source: brain/crm-export/*.csv
---

| Person key | Contact IDs | Company ID and domain | Origin employer, title, end date | Destination employer, domain, title, start date | Label or gap | Evidence case IDs and observed date | Rule ID | Event key or none | Company owner or gap | Task: proposed, suppressed, none, or owner gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Proposal rows

| Proposal path | Row | Record ID | Action | Event key | Evidence |
| --- | --- | --- | --- | --- | --- |

## Gaps for person

| Contact IDs | Missing or conflicting fact | Required follow-up |
| --- | --- | --- |
```

## Proposal task example

```markdown
---
skill: contact-move-routing
created_at: <YYYY-MM-DD>
status: proposed
approved_by:
---

| # | Object | Record ID | Field | Old value | New value | Reason | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | company | C003 | task for owner | (blank) | maria.ortiz: review Elena Price's verified role change and duplicate contact records | move-verified; event key: linkedin.example/in/example-elena-price \| harborledger.example \| harborledger.example \| 2026-08-01 | move-evidence.csv ROLE_M101/ROLE_M102; companies.csv C003; move-contacts.csv M101/M102 |
```
