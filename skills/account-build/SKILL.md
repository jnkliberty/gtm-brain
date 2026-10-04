---
name: account-build
description: "Use when vendor account candidates need matching against CRM companies, ICP screening, and revenue-based tiers before anyone creates records. Reads a live CRM or CSV export, checks duplicate domains and similar names, then writes a proposal for a person to approve."
license: MIT
---

# Account build

Turns a vendor list into reviewed account proposals. The skill owns the process; `brain/icp.md` and `brain/tiers.md` own the policy.

## Evidence and gaps

**Match** is the leading word. Cite each decision with a candidate ID, an existing company ID when relevant, exact column values, and the rule ID. A missing value or an ICP condition absent from the files stays a gap. A proposal is a request for review, never a claim that the account already exists in the CRM.

## Inputs

- `brain/crm-export/candidates-accounts.csv`: vendor candidates.
- `brain/crm-export/companies.csv`, or a live CRM read (see Connect).
- `brain/crm-export/README.md`, `brain/icp.md`, `brain/tiers.md`, and `brain/field-rules.md`.
- `brain/proposals/README.md`: proposal rows and approval boundary.

## Connect

When a live CRM connection is available, read companies only. Map its properties to the meanings in `brain/crm-export/README.md`; list unmapped properties as gaps. Otherwise use the CSV export. This skill reads either source and writes only a new proposal file. A person approves and applies CRM changes.

## Source check

Before a step uses a fact or proposes a value or record, find the fact's row in "Where to look" in `brain/sources.md` and apply its Conflict order. Cite the winning source's rule ID and read date. A fact with no row is a gap (`source-unmapped`). A copy older than its "Fresh for" days, counted to the date of the run, is stale. A vendor candidate holds detected values only; it never overrides a CRM company value. When company rows for one domain disagree on a value the match or tier uses with no winner, put the candidate under Escalated with both values, both dates, and the rule ID, and write no create row for it. When the export is stale, write no create row: put each unmatched candidate under Escalated with the export's age. Never pick one value silently, and keep this ranking in `brain/sources.md`, not here.

## Steps

1. **Read and match.** Read every candidate and current company. Normalize domains for comparison by lowercasing and removing a leading `www.`. A candidate with the same domain as an existing company is a match, not a create; list every matching company ID and flag existing duplicate IDs. A similar company name with a different domain is an escalation for a person to verify identity. The step is done when every candidate has a domain match, a possible name match, or neither, with both sides cited. Then apply the source check.
2. **Filter.** For candidates with neither match, apply each checkable condition in `brain/icp.md`. State the value behind each pass or fail. List founder-led or early sales motion and outbound/enrichment stack as gaps when the files do not record them. A clear fail is skipped; a candidate that passes checkable conditions can receive a conditional create proposal with its gaps attached. The step is done when every unmatched candidate is pass, fail, or ambiguous, with each ICP condition accounted for.
3. **Check revenue and tier.** For candidates eligible for a create proposal, divide annual revenue by employees and apply `tier-check-revenue-first`. Escalate any value outside the rule's range; write no tier or create row for it. Use `tier-confirmed-wins` for current companies when showing a comparison. Apply `tier-1`, `tier-2`, or `tier-3` only after the revenue check passes. The step is done when each eligible candidate has a cited tier or a cited reason no tier can be set.
4. **Propose and stop.** Write one new `brain/proposals/<today>-account-build-<topic>.md` using the format below and `brain/proposals/README.md`. Put create actions in proposal rows; put matched, skipped, and escalated candidates in the review sections. If that path exists, stop and report it without overwriting. The run is done when every candidate appears exactly once in a decision section and every create row has a tier, evidence, and unresolved ICP gaps.

## Write boundary

Write only a new file in `brain/proposals/`. Keep the candidate list, export, and CRM as read. A person verifies gaps and applies approved rows.

## Proposal format

```markdown
---
skill: account-build
created_at: <YYYY-MM-DD>
status: proposed
approved_by:
source: <CRM name (read-only) or brain/crm-export/companies.csv>
---

| # | Object | Record ID | Field | Old value | New value | Reason | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | company | <candidate ID> | create record | (blank) | <name, domain, fields, tier> | <ICP and tier rule IDs; conditional gaps> | <candidate row and quoted values> |

## Matched, no create
| Candidate | Existing company IDs | Domain evidence | Existing duplicate IDs |

## Skipped
| Candidate | ICP rule or condition | Evidence |

## Escalated
| Candidate | Reason | Evidence | Person to check |

## Gaps before approval
| Candidate | Missing ICP condition | Source checked |
```
