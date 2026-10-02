# Proposals

A proposal is a set of CRM changes a skill suggests and a person approves. Nothing in a proposal reaches a CRM until a person approves it; in this version no skill applies proposals at all.

File name: `<YYYY-MM-DD>-<skill>-<short-topic>.md`. A proposal file is never overwritten.

```markdown
---
skill: <skill name>
created_at: <YYYY-MM-DD>
status: proposed | approved | rejected
approved_by:
---

| # | Object | Record ID | Field | Old value | New value | Reason | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | company | C004 | revenue_detected | 500000000000 | (blank) | 90 employees cannot produce $500B | companies.csv C004 |
```

Use `(blank)` for an empty value. One row per field change. The old value is what the CRM held when the proposal was made.

For a record action, use one of these exact values in `Field`. Put the target record ID in `New value` for a merge. A task's `New value` names its owner and requested follow-up. Use `(blank)` for fields without a current value.

| Field | Object | Record ID | New value |
| --- | --- | --- | --- |
| `create record` | company or contact | candidate ID | Proposed record fields, including the candidate ID |
| `archive record` | contact | current contact ID | `restorable` |
| `merge into <id>` | company or contact | current record ID | Surviving record ID |
| `task for owner` | company or contact | current record ID | Owner and requested follow-up |

These rows are proposals. The person checks current values, approves, and applies them in the CRM.

- `stale-proposal`: when the CRM now holds something other than a row's old value, the record changed after the proposal was made. That row needs a fresh look before approval.
