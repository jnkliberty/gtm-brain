---
name: call-intel-to-themes
description: "Use when private sales call notes need an internal, evidence-backed pain theme. Confirm each excerpt on its own, resolve company domains, exclude conflicting claims, and report facts, hypotheses, and gaps without drafting outbound copy."
license: MIT
---

# Call intel to themes

Find recurring pain in private call notes. The result is an internal proposal for a person to review, never a public claim.

## Connect

For this CSV wave, read only the local files below, even when a live CRM or call connector is available. Do not call a connector. Take a review date and short topic from the person; for the starter fixture, use 2026-09-28 when no date is supplied.

## Inputs

- `brain/calls/call-notes.csv`: one exact excerpt per row, identified by `call_id` and `quote_id`.
- `brain/crm-export/companies.csv`: join `company_id` to its `domain`; never infer a domain from the company name. It is a copy: apply `brain/sources.md` and cite `source-export-copy` with its read date. When the export is older than its "Fresh for" days, state its age under Gaps and propose no theme from it; still report Facts and Gaps.
- `brain/call-rules.md`: `call-confirmed`, `call-claim`, `theme-two-domains`, `call-conflict`, `call-private`, and `draft-public-only`.
- `brain/field-rules.md` and `brain/crm-export/README.md`: check whether a field mentioned in a call has a documented CRM mapping.

## Steps

1. **Read each excerpt.** Keep its exact quote, `call_id`, `quote_id`, `company_id`, call date, source, `pain_key`, and `claim_value` together. Resolve `company_id` to a bare domain from `companies.csv`; an unknown ID or missing domain is a gap and cannot count. Apply `call-confirmed` to each row independently: `rep_confirmed=yes`, a valid `rep_confirmed_at` no later than the review date, and a quote that supports that row's `present` or `absent` value under `call-claim`. A confirmed quote elsewhere on the same call does not confirm this row. The step is done when every excerpt is marked confirmed, unconfirmed, or gap with its own reason and source row.
2. **Resolve conflicts.** Group excerpts by `call_id` and `pain_key` for the call readback, then compare all confirmed claims by resolved company domain and `pain_key`. If one domain has both confirmed `present` and `absent` claims for that pain, including across duplicate company IDs, apply `call-conflict`: list both exact quotes and exclude that domain's evidence for that pain until a person resolves it. The step is done when every opposing pair is visible and no conflicted domain contributes to a theme count.
3. **Count themes.** For each `pain_key`, count unique resolved company domains with eligible confirmed `present` excerpts. Repeated excerpts, duplicate company IDs at the same domain, unconfirmed excerpts, `absent` claims, and unresolved conflicts add zero domains. Apply `theme-two-domains`: propose a recurring theme only at two or more unique domains. Keep each domain's supporting quote and row ID beside the count. If none qualifies, write `none` and the evidence needed to revisit it. The step is done when every pain key has an eligible domain count and a proposed theme or `none`.
4. **Separate interpretation.** Put exact confirmed excerpts under Facts. Put interpretations and possible causes under Hypotheses, labeled as such. Put missing confirmation, unresolved conflicts, unknown domains, and fields without a documented CRM mapping under Gaps. Cite `call-private` and `draft-public-only` for the private boundary. Do not create a CRM field row from a call claim; a confirmed-field change belongs to a person under `brain/field-rules.md`. The step is done when every interpretation is labeled and every missing mapping remains a gap.
5. **Write and stop.** Create one new `brain/themes/<YYYY-MM-DD>-<short-topic>.md` using the format below. If the path exists, stop and tell the person; never overwrite it. Show the person the proposed theme, eligible domain count, conflicts, and gaps. The run is done when the file exists, every fact cites its own confirmation and source, and the file contains no outbound draft or published claim.

## Write boundary

Write only the new internal theme file. Leave the call notes, export, CRM, and proposals unchanged. For real calls, use a private repository; if the working tree is public, stop before writing private quotes and ask for a private workspace. A person decides whether any private fact may be used outside this review.

## Theme file format

```markdown
---
skill: call-intel-to-themes
reviewed_at: <YYYY-MM-DD>
source: brain/calls/call-notes.csv
status: proposed
---

## Proposed theme
<pain_key and plain-language theme, or none>
Eligible domains: <count and domains>; rule: theme-two-domains.

## Facts
| Pain key | Domain | Company ID | Call ID | Quote ID | Claim | Exact quote | Rep confirmed | Confirmed at | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <key> | <domain> | <ID> | <ID> | <ID> | present or absent | "<exact excerpt>" | yes | <date> | <source> |

## Other excerpts
| Call ID | Quote ID | Pain key | Exact quote | Status and reason | Source |

## Domain counts
| Pain key | Eligible domains | Count | Result | Evidence quote IDs |

## Conflicts
- <resolved domain and pain key>: <opposing company IDs, quote IDs, and exact quotes>; excluded by call-conflict.

## Hypotheses
- <interpretation, clearly labeled hypothesis; cite the supporting quote IDs>

## Gaps
- <missing confirmation, unresolved conflict, unknown domain, or unmapped CRM field; cite row or rule>

## Private boundary
Internal review only (`call-private`, `draft-public-only`). External use needs separate human clearance.
```
