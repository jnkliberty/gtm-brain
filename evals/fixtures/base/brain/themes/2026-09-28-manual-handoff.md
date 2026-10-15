---
skill: call-intel-to-themes
reviewed_at: 2026-09-28
source: brain/calls/call-notes.csv
status: proposed
---

## Proposed theme
manual_handoff: sales sees a handoff note only after a person copies or retypes it between systems.
Eligible domains: 2 (harborledger.example, summitfleet.example); rule: theme-two-domains.

## Facts
| Pain key | Domain | Company ID | Call ID | Quote ID | Claim | Exact quote | Rep confirmed | Confirmed at | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manual_handoff | harborledger.example | C003 | CALL-01 | Q001 | present | "We copy handoff notes into three places before sales sees them." | yes | 2026-09-09 | brain/calls/call-notes.csv row Q001; domain from brain/crm-export/companies.csv, read 2026-09-28 (source-export-copy) |
| manual_handoff | summitfleet.example | C010 | CALL-02 | Q003 | present | "We retype qualification notes before the account owner sees them." | yes | 2026-09-13 | brain/calls/call-notes.csv row Q003; domain from brain/crm-export/companies.csv, read 2026-09-28 (source-export-copy) |

## Other excerpts
| Call ID | Quote ID | Pain key | Exact quote | Status and reason | Source |
| --- | --- | --- | --- | --- | --- |
| CALL-01 | Q002 | manual_handoff | "I think the owner also waits a day for those notes." | Unconfirmed: rep_confirmed is no (call-confirmed) | brain/calls/call-notes.csv row Q002 |
| CALL-03 | Q004 | quote_delay | "Our quote approval takes four days." | Confirmed, but C001 and C002 share northwindrobotics.example: one domain | brain/calls/call-notes.csv row Q004 |
| CALL-04 | Q005 | quote_delay | "Quote approval usually takes three days for our team." | Confirmed, but C001 and C002 share northwindrobotics.example: one domain | brain/calls/call-notes.csv row Q005 |
| CALL-05 | Q006 | manual_handoff | "We copy every handoff note into the CRM." | Confirmed, excluded by call-conflict with Q007 | brain/calls/call-notes.csv row Q006 |
| CALL-05 | Q007 | manual_handoff | "We never copy handoff notes into the CRM." | Confirmed, excluded by call-conflict with Q006 | brain/calls/call-notes.csv row Q007 |
| CALL-06 | Q008 | support_sync | "We copy support status into the CRM every week." | Confirmed, excluded by call-conflict with Q009 | brain/calls/call-notes.csv row Q008 |
| CALL-07 | Q009 | support_sync | "We never copy support status into the CRM." | Confirmed, excluded by call-conflict with Q008 | brain/calls/call-notes.csv row Q009 |

## Domain counts
| Pain key | Eligible domains | Count | Result | Evidence quote IDs |
| --- | --- | --- | --- | --- |
| manual_handoff | harborledger.example, summitfleet.example | 2 | Proposed theme | Q001, Q003 |
| quote_delay | northwindrobotics.example | 1 | none: needs a second unique domain | Q004, Q005 |
| support_sync | none | 0 | none: the one domain is in conflict | none |

## Conflicts
- tidewateranalytics.example, manual_handoff: C008 quotes Q006 ("We copy every handoff note into the CRM.") and Q007 ("We never copy handoff notes into the CRM."); excluded by call-conflict.
- northwindrobotics.example, support_sync: C001 quote Q008 ("We copy support status into the CRM every week.") and duplicate C002 quote Q009 ("We never copy support status into the CRM."); excluded by call-conflict.

## Hypotheses
- Hypothesis: a buyer who already retypes notes between systems (Q001, Q003) may ask whether a new system adds one more copy step. Buyers would then put that doubt into a question about connecting to the systems they already run.

## Gaps
- Q002 has no rep confirmation.
- C008 needs a person to resolve Q006 against Q007.
- northwindrobotics.example needs a person to resolve Q008 against Q009.
- The CRM export has no field for handoff notes copied by hand (brain/field-rules.md and brain/crm-export/README.md map none).

## Private boundary
Internal review only (`call-private`, `draft-public-only`). External use needs separate human clearance. The excerpts are the starter's invented notes; no real call is quoted.
