---
name: crm-field-provenance
description: "Use when CRM values need checking against the line between machine values and human values in brain/field-rules.md. Two branches: review a proposal file of CRM changes before a person approves it, or audit a CRM export for confirmed values with no date and detected values that disagree with confirmed ones. Writes a review file; never edits or approves the proposal."
license: MIT
---

# CRM field provenance

Guards the line between values a machine detected and values a person confirmed. The skill owns the process. The team's policy lives in `brain/field-rules.md`, so a team changes a field pair or a rule by editing that file, never this one.

## Provenance and evidence

**Provenance** is the leading word: every value comes from a machine or a person, and the field it sits in says which.

- A **detected** field holds a machine value. Automation may write it.
- A **confirmed** field holds a person's value, with its **confirmation date** beside it. Only a person changes either.
- A **field pair** is one row of the table in `brain/field-rules.md`, with its rule ID (for example `field-revenue`).

Every finding cites **evidence**: the rule ID it rests on (`rule-no-overwrite`, `rule-confirmed-wins`, `rule-dated`, `rule-disagree`), the field pair ID, and the row it came from (proposal row number, or record ID in the export). A value no file holds is a **gap**: write it as a gap and leave it open.

## Connect

When a live CRM connection is available (for example a HubSpot, Salesforce, or Attio MCP server or API), read field values from it, read-only. Map each CRM field to its column in `brain/crm-export/README.md`; a field pair you cannot map is a gap. Otherwise ask the person for an export in the `brain/crm-export/README.md` format. Wave 1 reads only; every change goes to a person.

## Inputs

- `brain/field-rules.md`: the field pairs and the four rules.
- Current values: a live CRM connection, or `brain/crm-export/companies.csv` and `contacts.csv`.
- Branch A only: one proposal file in `brain/proposals/`, in the `brain/proposals/README.md` format.

## Branch A: review a proposal

1. **Read.** Read `brain/field-rules.md`, the proposal, and the current values for every record ID the proposal names. Identify record actions by the exact `Field` values in `brain/proposals/README.md`; their candidate IDs may have no current CRM record. The step is done when every field-change row is matched to a field pair and current record or listed as a gap, and every record-action row is identified.
2. **Judge each row.** Give each proposal row exactly one verdict. Identify `action` rows first; for field changes, `blocked` outranks `check`, and `check` outranks `ok`.
   - `blocked`: the row changes a confirmed field or its confirmation date. Rule: `rule-no-overwrite`. Note: "A person must make this change in the CRM themselves."
   - `check`: the row changes a detected field while the confirmed field holds a value. Rule: `rule-confirmed-wins`. Note: the change has no effect on anything that reads the value, because the confirmed value wins; quote the confirmed value.
   - `action`: the row proposes `create record`, `archive record`, `merge into <id>`, or `task for owner` as defined in `brain/proposals/README.md`. Rule: `record-action`. Note: a person reviews identity, current state, and approval before applying it; this is outside field provenance.
   - `check`: the row changes a field that no pair or rule in `brain/field-rules.md` covers, or a record the current values do not hold. Rule: `none`. Add the field to Gaps.
   - `check`: the row's old value differs from the current value, so the record changed after the proposal was made. Rule: `stale-proposal` (see `brain/proposals/README.md`). Note: both values; the row needs a fresh look before approval.
   - `ok`: the row changes a detected field, the confirmed field is empty, and the old value matches the current value. Rule: `rule-confirmed-wins`. Note: the new value becomes the value readers use.
   The step is done when the count of verdict rows equals the count of proposal rows. Test for a record action before testing whether its field has a pair.
3. **List gaps.** For each field-change row that no pair covers, add one line under Gaps: the object, the field, the proposal rows, and a suggestion to add a detected / confirmed / date pair for it to `brain/field-rules.md`. Record actions use `record-action` and need no field pair. The step is done when every `check` with rule `none` has its gap line.
4. **Write and stop.** Write the review file (format below). Show the person the `blocked` and `check` rows and the gaps. The run is done when the file exists and every row cites a rule ID and a proposal row.

## Branch B: audit the export

1. **Read.** Read `brain/field-rules.md` and the current values. The step is done when you can name, for each field pair, the export file and columns that hold it.
2. **Check every record.** For every record and every field pair:
   - The confirmed field holds a value and the date field is empty: finding under `rule-dated`. Note: "Owner to date or re-confirm."
   - Both the detected and confirmed fields hold a value and they disagree as `rule-disagree` defines it: numbers differ by more than 10% of the confirmed value; text differs at all, ignoring case and outer spaces. Finding under `rule-disagree`. Note: the confirmed value stands; the confirmed value may be stale or the enrichment source may be wrong.
   One record can produce both findings. The step is done when the count of records checked equals the count of records in the export, for every pair.
3. **Write and stop.** Write the review file (format below) and show the person the findings. The run is done when every finding carries the record ID, the field pair ID, both values, and the confirmation date or "(blank)".

## Write boundary

The skill writes only new files in `brain/provenance/`, creating the folder when it is missing. The proposal, the export, `brain/field-rules.md`, and the CRM stay exactly as they were: a person sets the proposal's status and makes every CRM change. When the review file name already exists, stop and tell the person; a review file is never overwritten.

## Review file format

Path: `brain/provenance/<today's date>-<proposal file name without .md>.md` for Branch A, or `brain/provenance/<today's date>-export.md` for Branch B.

```markdown
---
branch: proposal-review | export-audit
source: brain/proposals/<file> | brain/crm-export/companies.csv | <CRM name> (live, read-only)
reviewed_at: <YYYY-MM-DD>
counts: <n> ok, <n> check, <n> blocked, <n> action | <n> rule-dated, <n> rule-disagree
---

## Findings

Branch A:

| # | Proposal row | Record ID | Field | Old value | New value | Verdict | Rule | Field pair | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | C003 | revenue_confirmed | 25000000 | 41000000 | blocked | rule-no-overwrite | field-revenue | A person must make this change in the CRM themselves. |

Branch B:

| # | Rule | Record ID | Field pair | Detected value | Confirmed value | Confirmed at | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Gaps
- <object>.<field> (proposal rows <n>): no field pair covers it. Suggest adding a detected / confirmed / date pair to brain/field-rules.md.
```

Use `(blank)` for an empty value. Write "none" under Gaps when there are none.
