---
description: "The format of a change record: what changed, when, and the one metric that will judge it, declared before results come in. A person writes these; outcome-readback reads them. Read it before you record a change or run a readback."
---

# Change records

A change record says what a team changed and how it will judge the change. A person writes it before the first touch of the changed version goes out. `outcome-readback` reads it; no skill writes or edits it.

File name: `<YYYY-MM-DD>-<change-id>.md`, dated by `changed_at`. Tag every outbound touch sent under the change with the same `change_id` in `brain/crm-export/touches.csv`.

```markdown
---
change_id: <short-id>
changed_at: <YYYY-MM-DD>
what_changed: <one line: the play, draft rule, list filter, or page, and how it changed>
primary_metric: reply-rate | positive-reply-rate | meeting-rate
declared_at: <YYYY-MM-DD>
owner: <person>
---
```

- `primary_metric` is one metric from `readback-metrics` in [readback-rules.md](../readback-rules.md). Pick it before anyone looks at results.
- `declared_at` is the date the metric was written down. It must be on or before the first candidate touch (`readback-declared`). Never move it later or earlier after the fact; write a new change record instead.
- The opt-out rate is always checked as a guard; it needs no field.

[2026-09-15-ops-title-filter.md](2026-09-15-ops-title-filter.md) is an invented example.
