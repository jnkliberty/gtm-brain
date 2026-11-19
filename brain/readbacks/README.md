---
description: "The format of an outcome readback: one proposed decision on one change, with the people counts for both windows, the guard, the confounders, and the gaps. outcome-readback writes them; a person approves them. Read it before you write or review a readback."
---

# Readbacks

A readback is the answer to "did this change work?" for one change record in [changes/](../changes/). `outcome-readback` writes one new file per run, named `<YYYY-MM-DD>-<change-id>.md` with the run date. A readback file is never overwritten. [readback-rules.md](../readback-rules.md) holds every rule ID a readback cites.

```markdown
---
skill: outcome-readback
change_id: <change-id>
created_at: <YYYY-MM-DD>
status: proposed
approved_by:
decision: promote | keep-testing | roll-back | unproven
rule: <the readback-decide line and rule ID that decided>
primary_metric: <metric from the change record, or gap>
export_read_date: <YYYY-MM-DD, or gap>
---
```

The body has these sections, in order: Decision, Counts, Guard, Confounders, Proposed edit, Evidence, Gaps. Counts is one table with a row per window: dates, people sent, people who bounced only, delivered people, the primary metric as "n of N" with the percent, and the opt-out rate the same way. Proposed edit reads `none` unless the decision is `promote`.

A person approves a readback by setting `status` and `approved_by`. Approval changes nothing else: the person makes any proposed edit to a play or rule file by hand.
