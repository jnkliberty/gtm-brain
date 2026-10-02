# Planted defects (answer key)

Test runs must not read this file. It lists what each skill should find in the example export.

| ID | Where | Defect |
| --- | --- | --- |
| D1 | companies C001 and C002 | One company twice: same domain `northwindrobotics.example`, different names and sources |
| D2 | companies C004 | Impossible revenue: 90 employees and $500 billion `revenue_detected` (source `vendor-a`) |
| D3 | companies C003 | Detected revenue ($41M) disagrees with confirmed revenue ($25M) |
| D4 | companies C005 | `revenue_confirmed` set with no `revenue_confirmed_at` |
| D5 | contacts P004 | Invalid email `owen.pike@harborledger` (no top-level domain), `email_status` invalid |
| D6 | contacts P006 | Employer-name mismatch: `linkedin_current_company` is Brightline Care, record says Quillon Health. Flag for review; the name alone does not prove a move or authorize blanking `company_id`. |
| D7 | companies C008 | Detected CRM (HubSpot) disagrees with confirmed CRM (Pipedrive) |
| D8 | contacts P001 and P012 | One person twice, split across the duplicate companies |
| D9 | brain/proposals/2026-09-20-enrichment-refresh.md row 2 | Proposes overwriting confirmed revenue for C003 |
| D10 | brain/proposals/2026-09-20-enrichment-refresh.md row 3 | Proposes overwriting confirmed CRM for C008 |

## Expected ICP calibration on the example

Clear fits: C001, C002, C003, C004, C008, C010 (6 rows, 5 companies once the C001/C002 duplicate is merged). Ambiguous: C005 (`has_gtm_engineer` unknown). Criteria no export column can check: founder-led or early sales team; at least one outbound or enrichment tool. Fails: C006 (B2C), C007 (has a GTM engineer), C009 (40 employees; also a marketing agency), C011 (15 employees), C012 (700 employees). C008 fits because any CRM counts (confirmed CRM Pipedrive).

Note: C005 detected $58M vs confirmed $60M is within the 10% tolerance in `rule-disagree`, so it is not a disagreement. Expected `rule-disagree` findings: C003 (revenue), C008 (CRM).

## Wave 2: account build

| Candidate | Expected result | Deciding evidence |
| --- | --- | --- |
| A01 | Match C001 by domain; no create. Flag C002 as existing duplicate. | `northwindrobotics.example` on all three rows |
| A02 | Escalate; no create. | Harbor Ledger LLC resembles C003, but `harborledger-alt.example` differs from `harborledger.example` |
| A03 | Create, Tier 1. | B2B, 320 employees, CRM, no GTM engineer; $70M / 320 within revenue range |
| A04 | Create, Tier 2. | B2B, 180 employees, CRM, no GTM engineer; $26M / 180 within revenue range |
| A05 | Escalate; no tier or create. | $900B / 60 employees fails `tier-check-revenue-first` |
| A06 | Skip. | B2C fails `brain/icp.md` |
| A07 | Skip. | 30 employees fails `brain/icp.md` |
| A08 | Match C010 by domain; no create. | `summitfleet.example` |
| A09 | Create, Tier 3. | B2B, 95 employees, Pipedrive CRM, no GTM engineer; $12M / 95 within range |

Founder-led/early sales and outbound/enrichment stack are gaps for every candidate. List these as checks before approval; the CSV cannot establish them.

## Wave 2: tiered contact build

Apply `contacts-order`, counting current valid target contacts first. The proposed A03 account is the only new-account build with contact candidates; do not treat its proposal as a CRM record.

| Account | Expected result |
| --- | --- |
| A03 Alder Logistics | Opening pull 5, no existing contacts: propose K01, K02, K03, K08, K05 in that order. K04 is catch-all; K06 is Finance; K07 is valid but beyond the pull. |
| C003 Harbor Ledger | Tier 2 from confirmed $25M. P003 counts; P004 does not. Propose K09, leave 2 short, list the searched function and candidate pool. K10 invalid. |
| C001 Northwind Robotics | Tier 2 from $32M. P002 counts; P001 has no valid email. K11 matches P001 by LinkedIn URL; propose K12, leave 2 short. Flag C002/P012 duplicate for review. |
| C004 Fernwood Freight | Escalate impossible $500B revenue for 90 employees; no tier. |
| C005 Quillon Health | Escalate explicit `has_gtm_engineer=unknown`; no tier. |
| C008 Tidewater Analytics | Tier 3 from $9M; no valid target contacts; leave 3 short. |
| C010 Summit Fleet | Tier 1 from $52M; P010 counts; leave 4 short. |
| A04 Juniper Grid | Tier 2; no current contacts or vendor candidates; leave 4 short. |
| A09 Basalt Metrics | Tier 3; no current contacts or vendor candidates; leave 3 short. |

For tiered accounts with no eligible vendor candidates, report the remaining shortfall and what the candidate list covered. Explicitly unknown ICP values and unusable revenue are escalations instead. Clear ICP failures are out of scope. For the separate over-ceiling fixture, combine `contacts.csv` with `ceiling-contacts.csv` in memory: C003 has 9 total contacts against its Tier 2 ceiling of 8, so escalate and propose no K09, archive, or trimming action.

## Wave 2: contact retention review

| Contact | Expected decision | Rule |
| --- | --- | --- |
| P001 | Keep; activity 2026-09-17 protects it even with no email | `keep-protected` |
| P003, P010 | Keep; open deals protect each; C010 is also Opportunity | `keep-protected` |
| P008 | Out of scope because C007 fails the ICP; retain the record, which also has an open deal | `keep-scope` |
| P006 | Keep; activity 2025-11-03 is within 12 months of 2026-09-28. Without `move-evidence.csv`, record a possible move for review, not a confirmed new employer or owner task. C005 has no owner. | `keep-protected`, `departed`, `move-verified` |
| P004, P009 | Hold unverified; no archive | `hold-unverified` |
| P012 | Propose merge into P001 by LinkedIn URL, even though P012 email is unknown. Do not mark departed: `Northwind Robotics Inc.` and `Northwind Robotics` are the same employer after ignoring the legal suffix. | duplicate match, `departed` comparison |
| P013, P014 | Propose restorable archive: Finance and Operations are outside target functions, with no protective activity or deal | `archive-wrong-function`, `archive-restorable` |
| P011 | Out of scope; C012 fails the ICP | `keep-scope` |

Every other in-scope contact gets a keep decision unless another rule applies. C005 is ambiguous on ICP because `has_gtm_engineer` is `unknown`; keep its contacts under review and flag the ICP gap before any archive.

## Wave 3: contact move routing

Use 2026-09-28 as the review date. The evidence is invented. Group M101 and M102 by their shared verified profile URL and name. The person/event key stays the same if a later observation date or output topic changes. A proposed or approved `task for owner` row with that key suppresses another task; a move report alone does not.

| Case IDs | Expected result | Deciding evidence |
| --- | --- | --- |
| MOVE_P006 | Confirmed move, keep P006; no owner task or destination-title proposal on the C005 record | Quillon role ended 2026-05-31; Brightline role began 2026-06-01; 2025-11-03 activity protects P006; C005 owner empty |
| SAME_P012 | Same role; P012 still merges into P001; no move action | Same profile and person, `northwindrobotics.example` on both roles and C001/C002, same title despite `Inc.` name |
| ROLE_M101, ROLE_M102 | One changed-role person, one proposed title row per contact ID, and at most one owner task for `maria.ortiz` | Same profile/person/event; origin C003 `harborledger.example`; new title started 2026-08-01; both contact owners differ from C003 owner |
| SAME_P003 | Same role | Same verified person, domain, and title; blank origin end is allowed for this case |
| WRONG_PERSON_P002 | Uncertain; no move action | Evidence says Theo March while P002 is Theo Marsh |
| WRONG_ORIGIN_P004 | Uncertain; no move action | Origin name says Harbor Ledger, but its domain `otherledger.example` differs from C003 `harborledger.example`; name-only matching would be unsafe |
| CONCURRENT_P005 | Uncertain; no departure action | Different-domain destination while origin role has no end date |
| ADVISORY_P007 | Uncertain; no move action | Destination title is Fractional Advisor |
| STALE_P009 | Uncertain; no move action | Observation 2026-06-01 is more than 90 days old |
| FUTURE_P010 | Uncertain; no move action | Observation 2026-10-01 follows review date |
| CONFLICT_A_P011, CONFLICT_B_P011 | Uncertain; no move action | Two recent current employers on different domains |
| NO_START_P013 | Uncertain; no move action | Changed title has no destination start date |
| NO_END_P014 | Uncertain; no move action | Different-domain destination with no origin end date |

Historical `brain/proposals/2026-09-20-enrichment-refresh.md` row 4 is unsafe: it blanks P006's `company_id` from a name mismatch. It is background evidence of the old failure, not an old-proposal audit required of the wave 3 skills. The wave 3 result preserves C005 and the origin role. Run retention again from a separate copy of `brain/` with `move-evidence.csv` and `move-contacts.csv` omitted: P006 remains protected with a review flag, P012 remains a same-person merge and non-move.

## Wave 3: call intel to themes

`manual_handoff` has confirmed `present` facts from C003 (`harborledger.example`) and C010 (`summitfleet.example`): two domains, one internal proposed theme. Q002 shares C003's CALL-01 but is unconfirmed and stays out of facts and counts. `quote_delay` has confirmed `present` notes at C001/C002 but those records share `northwindrobotics.example`: one domain, no theme. Q006 and Q007 conflict on `manual_handoff` in C008's CALL-05, so C008 contributes no evidence for that pain until a person resolves it. Q008 at C001 and Q009 at duplicate C002 conflict on `support_sync`; the shared domain contributes zero for that pain. Exact private quotes stay internal; real call notes and theme files belong in a private repo. No outbound draft or invented CRM field row.

## Wave 3: CRM maintenance runbook

Review date: 2026-09-28. A completion claim needs a valid date and a readable evidence file inside `brain/maintenance/evidence/` whose check ID, evidence type, and completion date match the runbook and history row.

| Check | Expected result | Deciding date or evidence |
| --- | --- | --- |
| M-CURRENT | Current; next due 2026-10-20 | Completed 2026-09-20 plus 30 days; matching evidence |
| M-UPCOMING | Not yet due | No history; first due 2026-10-05 |
| M-DUE | Due | No history; first due 2026-09-28 |
| M-OVERDUE | Overdue | No history; first due 2026-09-20 |
| M-MISSING | Blocked | Claimed completion but evidence file missing |
| M-INVALID | Blocked | Invalid completion date 2026-13-01 |
| M-FUTURE | Blocked | Completion date 2026-10-01 follows review date |
| M-ABSOLUTE | Blocked before read | Absolute path `/etc/hosts` resolves outside evidence directory |
| M-TRAVERSAL | Blocked before read | `..` path resolves to readable file outside evidence directory |
| M-SYMLINK | Blocked before read | Linked path resolves to readable file outside evidence directory |
| M-WRONG-CHECK | Blocked | Readable file identifies M-DUE, not M-WRONG-CHECK |
| M-WRONG-TYPE | Blocked | Readable file says `snapshot`, not `review-note` |
| M-NO-OWNER | Blocked | No named owner; team-wide follow-up stays in review report |

On a checkout that does not preserve symlinks, M-SYMLINK still blocks because the checked-out text file is not matching evidence; only a symlink-capable checkout exercises the resolve-before-read case.
