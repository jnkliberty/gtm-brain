---
name: tiered-contact-build
description: "Use when accounts need an opening set of verified contacts by tier. Counts existing target-function contacts, checks duplicate people and valid email, selects vendor candidates in the team's function order, and writes create proposals and shortfalls for a person to approve."
license: MIT
---

# Tiered contact build

Fills an account's opening contact pull from verified candidates. `brain/contact-rules.md` sets functions, order, pulls, and ceilings.

## Evidence and gaps

**Count** is the leading word. Show the existing qualifying IDs, their email statuses, the tier calculation, and the candidate IDs searched. Cite each selected or rejected row and its rule ID. A missing email or unmapped CRM field stays a gap; it never becomes a valid contact by assumption.

## Inputs

- Current companies and contacts from `brain/crm-export/companies.csv` and `contacts.csv`, or a live CRM read.
- `brain/crm-export/candidates-contacts.csv`; proposed new companies in a current `account-build` proposal when supplied.
- `brain/crm-export/README.md`, `brain/icp.md`, `brain/tiers.md`, `brain/contact-rules.md`, and `brain/field-rules.md`.
- `brain/proposals/README.md`.

## Connect

When a live CRM connection is available, read companies and contacts only and map properties to `brain/crm-export/README.md`. Otherwise use the CSV export. A proposed new account remains a candidate until a person creates it; label its contact rows as dependent on that approval. This skill writes only a new proposal file, never to a CRM.

## Steps

1. **Scope and tier.** Include every current company that passes the checkable ICP conditions and every proposed new account supplied for this run. Group duplicate company IDs by domain; count their contacts together. Apply `tier-confirmed-wins`, then `tier-check-revenue-first`, then a tier rule. Put clear ICP failures under Out of scope. Escalate an explicit unknown ICP value or impossible revenue instead of assigning a tier. The step is done when every current and proposed account has a tier, an out-of-scope reason, or an escalation, each with cited values.
2. **Audit current contacts.** For each tiered account, count distinct existing people in `contacts-functions` with `email_status=valid`; match company IDs in the same domain group. Find duplicate people by LinkedIn URL, then name plus company domain when URL is empty; count a duplicate group once and flag its IDs for review. List contacts excluded by function or email status. Compare the number of all current contact records with `contacts-ceiling`; when it exceeds the ceiling, escalate to the owner and propose no trimming or additions. The step is done when each tiered account has an existing valid target count, a ceiling comparison, and the IDs behind both.
3. **Select candidates.** Match candidates by company domain. Deduplicate against current and candidate people by LinkedIn URL, then by name plus company domain when URL is empty. Exclude non-target functions and any email status other than `valid`. Sort eligible candidates by `contacts-order`: RevOps, Sales, Marketing, Executive; within a function, more senior titles first, then candidate ID for a tie. Propose only enough new contacts to reach `contacts-opening-pull`, unless the ceiling leaves fewer slots. The step is done when every vendor candidate at a tiered account is selected or has a cited exclusion reason, and the selected order can be reproduced.
4. **Report shortfalls and stop.** Write one new `brain/proposals/<today>-tiered-contact-build-<topic>.md` in the format below. Record every tiered account left below its opening pull, the functions and candidate rows searched, and the number still needed. An account with no candidates still gets a shortfall row. If the path exists, stop without overwriting. The run is done when every tiered account has an opening count, proposed count, remaining shortfall, and ceiling status.

## Write boundary

Write only a new file in `brain/proposals/`. A person checks account identity, unresolved ICP gaps, and current CRM values before applying any proposal.

## Proposal format

```markdown
---
skill: tiered-contact-build
created_at: <YYYY-MM-DD>
status: proposed
approved_by:
source: <CRM name (read-only) or brain/crm-export/*.csv>
---

| # | Object | Record ID | Field | Old value | New value | Reason | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | contact | <candidate ID> | create record | (blank) | <person, company ID or proposed account ID, email, function> | <tier, count, order; dependency if new account> | <candidate row; existing contact IDs; rule IDs> |

## Account counts and shortfalls
| Account | Tier evidence | Existing valid target IDs | Opening pull | Proposed IDs in order | Remaining | Ceiling status | Searched |

## Excluded candidates
| Candidate | Reason | Evidence |

## Existing duplicates for review
| Account | Contact IDs | Match evidence | Counted as |

## Escalated accounts and gaps
| Account | Reason | Evidence | Person to check |

## Out of scope
| Account | ICP failure | Evidence |
```
