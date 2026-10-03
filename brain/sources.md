# Sources

Where each kind of fact lives, and which place wins when two disagree. `account-handoff` reads it on every run. The other skills in this starter do not read it yet. Every system, owner, and date below is invented. Replace them with your own.

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

The snapshot date of `brain/crm-export/` is the read date of every value taken from it. "Last checked" is the date someone last reviewed the row itself.

| Fact | Truth lives in | Owner | How skills read it | Last checked |
| --- | --- | --- | --- | --- |
| Deal stage, amount, and owner | CRM | Sales lead | `brain/crm-export/`, snapshot dated 2026-09-28 | 2026-09-28 |
| Company and contact records | CRM | Sales lead | `brain/crm-export/`, snapshot dated 2026-09-28 | 2026-09-28 |
| Column meanings | `brain/crm-export/README.md` | Operations | File read | 2026-09-28 |
| Detected and confirmed values | `brain/field-rules.md` | Operations | File read | 2026-09-28 |
| Who we sell to | `brain/icp.md` | Marketing lead | File read | 2026-09-21 |
| Stage definitions and handoff rules | `brain/stages.md` | Sales lead | File read | 2026-09-21 |
| Plays and draft rules | `brain/plays.md` | Marketing lead | File read | 2026-09-21 |
| Tiers | `brain/tiers.md` | Sales lead | File read | 2026-09-21 |
| Call excerpts | Call recorder | Sales lead | `brain/calls/call-notes.csv`, private copy | 2026-09-24 |
| Account history and marketing activity | `brain/accounts/` | Account owner | File read | 2026-09-24 |
| Signals on accounts | `brain/signals/` | Marketing lead | File read | 2026-09-24 |
| Decisions and verdicts | `brain/decisions/` | The person who gave the verdict | File read | 2026-09-24 |

## Conflict order

When two places disagree, the first matching rule decides.

1. **`source-crm-live`:** the CRM wins for live status: stage, amount, owner, close date.
2. **`source-brain-rules`:** this repo wins for rules, definitions, and reviewed decisions.
3. **`source-recorder`:** the call recorder wins for what was said.
4. **`source-export-copy`:** an export, a snapshot, or a value copied into a brain file is a copy. State its read date beside every value read from it. When two copies disagree, the one read later wins. When their read dates are equal or one is missing, neither wins and the field stays unresolved.
5. **`source-fix-copy`:** when a copy disagrees with its source, report the disagreement and propose an update to the copy. Keep the decision based on the source.
6. **`source-unmapped`:** a fact with no row in "Where to look" is a gap. List it under Gaps and name the row that would resolve it.
