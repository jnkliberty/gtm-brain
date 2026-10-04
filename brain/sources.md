# Sources

Where each kind of fact lives, which place wins when two disagree, and how fresh a copy must be. This is the one source-authority policy. Every skill that reads, proposes, or audits CRM data reads it before it proposes a value or a record. A skill keeps only its own safeguards and never ranks sources itself. Edit this file to change who wins. Dated evidence stays in its own files (`brain/crm-export/` snapshots, `brain/decisions/`, `brain/audits/`, `brain/provenance/`); editing this file never rewrites it. Every system, owner, and date below is invented. Replace them with your own.

## Surfaces

| Surface | Belongs here | Lives elsewhere | Authority |
| --- | --- | --- | --- |
| CRM | Deal stage, amount, owner, close date, contact records | Rules, definitions, call excerpts | Live status of accounts, contacts, and deals |
| This repo (`brain/`) | ICP, stages, plays, tiers, field rules, account history, signals, decisions, corrections | Live deal status, raw transcripts | Rules, definitions, and reviewed decisions |
| `brain/crm-export/` | A dated snapshot of CRM companies and contacts | Anything edited by hand | A copy. It holds no authority. |
| Call recorder | Full recordings and transcripts | Themes, decisions | What was said on a call |
| Enrichment vendor | Detected company and contact values | Values a person confirmed | Detected values only (see `brain/field-rules.md`) |
| Chat and email threads | Requests, approvals in progress | Any fact a skill relies on | None. A fact from chat enters the brain as a gap until it lands in a surface above. |

## Where to look

The snapshot date of `brain/crm-export/` is the read date of every value taken from it. "Fresh for" is how many days a copy stays current, counted from its read date to the date of the run. A copy older than that is stale. "Last checked" is the date someone last reviewed the row itself.

| Fact | Truth lives in | Owner | How skills read it | Fresh for (days) | Last checked |
| --- | --- | --- | --- | --- | --- |
| Deal stage, amount, and owner | CRM | Sales lead | `brain/crm-export/`, snapshot dated 2026-09-28 | 30 | 2026-09-28 |
| Company and contact records | CRM | Sales lead | `brain/crm-export/`, snapshot dated 2026-09-28 | 30 | 2026-09-28 |
| Column meanings | `brain/crm-export/README.md` | Operations | File read | no limit | 2026-09-28 |
| Detected and confirmed values | `brain/field-rules.md` | Operations | File read | no limit | 2026-09-28 |
| Who we sell to | `brain/icp.md` | Marketing lead | File read | no limit | 2026-09-21 |
| Stage definitions and handoff rules | `brain/stages.md` | Sales lead | File read | no limit | 2026-09-21 |
| Plays and draft rules | `brain/plays.md` | Marketing lead | File read | no limit | 2026-09-21 |
| Tiers | `brain/tiers.md` | Sales lead | File read | no limit | 2026-09-21 |
| Contact retention and build rules | `brain/contact-rules.md` | Sales lead | File read | no limit | 2026-09-21 |
| Vendor account and contact candidates | Enrichment vendor | Operations | `brain/crm-export/candidates-*.csv`; a candidate is not a CRM record | 30 | 2026-09-28 |
| Contact work history | Enrichment vendor | Operations | `brain/crm-export/move-evidence.csv`, each row dated by `observed_at`; `move-verified` in `brain/contact-rules.md` sets its limit | 90 | 2026-09-28 |
| Call excerpts | Call recorder | Sales lead | `brain/calls/call-notes.csv`, private copy | no limit | 2026-09-24 |
| Account history and marketing activity | `brain/accounts/` | Account owner | File read | no limit | 2026-09-24 |
| Signals on accounts | `brain/signals/` | Marketing lead | File read | no limit | 2026-09-24 |
| Decisions and verdicts | `brain/decisions/` | The person who gave the verdict | File read | no limit | 2026-09-24 |

## Conflict order

When two places disagree, the first matching rule decides.

1. **`source-crm-live`:** a value read live from the CRM wins for live status: stage, amount, owner, close date. An export is a copy, not a live read; `source-export-copy` covers it.
2. **`source-brain-rules`:** this repo wins for rules, definitions, and reviewed decisions.
3. **`source-recorder`:** the call recorder wins for what was said.
4. **`source-export-copy`:** an export, a snapshot, or a value copied into a brain file is a copy. State its read date beside every value read from it. When two copies disagree, the one read later wins. When their read dates are equal or one is missing, neither wins and the field stays unresolved. A copy older than its "Fresh for" days is stale: state its age and ask for a fresher read. A stale copy cannot support a proposal that depends on it.
5. **`source-fix-copy`:** when a copy disagrees with its source, report the disagreement and propose an update to the copy. Keep the decision based on the source.
6. **`source-unmapped`:** a fact with no row in "Where to look" is a gap. List it under Gaps and name the row that would resolve it.

## When no source wins

When the order above picks no winner, or the only value is stale, a skill reports both values, both read dates, and the rule ID. It proposes nothing for that field until a person resolves it at the source. It never picks one value silently.

Inside one record, `brain/field-rules.md` decides between a detected and a confirmed value. This file decides between places.
