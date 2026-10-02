---
name: data-accuracy-audit
description: "Use for the monthly accuracy audit of CRM accounts and contacts: samples records, checks each field the data allows, scores the checked fields against the team's bar, and traces every error to the source that produced it. Also use before trusting a report or filter built on CRM data, or after a new vendor import. Proposes fixes to the source, not the record."
license: MIT
---

# Data accuracy audit

Tells the team how far to trust its CRM data, and which source to fix. The rule: **fix the source, not the record**. One bad record is a symptom; the vendor, form, or habit that produced it will produce the next one.

## Evidence, checks, and gaps

**Evidence** is the leading word. Every error cites the file, the record ID, the field, and the value quoted as the export holds it.

- A **check** is a test the export itself can settle: a format, a comparison between two fields, a duplicate, a rule in `brain/field-rules.md`. Each check ends `pass` or `fail`.
- A **human check** is a field whose truth lives outside the export, for example whether a title is current, a stage, an owner, an industry, or `has_gtm_engineer`. It is listed as `needs human check` and left out of the score.
- An **empty** field is reported as empty and left out of the accuracy score. Emptiness is a completeness number, reported beside it.
- A **gap** is anything the audit needs that no file states, such as which enrichment tool wrote a detected value on a `manual` record. It stays a gap.

## Connect

When a live CRM connection is available (for example a HubSpot, Salesforce, or Attio MCP server or API), read companies and contacts from it, read-only, and map its fields to the columns in `brain/crm-export/README.md`. A column with no matching CRM field is a gap. Otherwise ask the person for an export in that format. Wave 1 never writes to a CRM.

## Inputs

- `brain/crm-export/companies.csv` and `contacts.csv`, or the live read above.
- `brain/crm-export/README.md`: what each column means and its allowed values.
- `brain/field-rules.md`: the detected and confirmed field pairs and their rule IDs.
- Team settings, given by the person at run time. Defaults: 25 accounts, 25 contacts, pass at 80% of checked fields, revenue per employee between $20K and $2M, detected and confirmed revenue agreeing within 10%.

## Checks

Duplicate checks compare each sampled record against the whole export, not only the sample.

| Object | Field | Fails when |
| --- | --- | --- |
| company | `domain` | not a bare `name.tld` (no scheme, path, or spaces) |
| company | `segment` | not `B2B` or `B2C` |
| company | `revenue_detected` | revenue divided by `employees` falls outside the team range |
| company | `revenue_detected`, `crm_detected` | disagrees with the confirmed value (`rule-disagree`; confirmed stands by `rule-confirmed-wins`, so the detected field fails) |
| company | `revenue_confirmed`, `crm_confirmed` | holds a value with an empty `_confirmed_at` date (`rule-dated`) |
| company | duplicate | another company has the same `domain` |
| contact | `email` | wrong shape, domain differs from its company's `domain`, or `email_status` is `invalid`. One fail per email; list every reason. |
| contact | `email_status` | `unknown`, `catch-all`, or empty: record as unverified, a human check |
| contact | `company_id` | missing from `companies.csv`, or `linkedin_current_company` names a different employer than that company's `name` (ignore suffixes like Inc.) |
| contact | duplicate | another contact has the same `linkedin_url`, or the same first and last name at the same company domain |

## Steps

1. **Sample.** Sort each file by ID, ascending. With N records and a sample size n, set k = N divided by n, rounded down, and take rows 1, 1+k, 1+2k, and so on until you hold n records. When N is n or fewer, audit every record and say so. The step is done when the audit file can state N, n, k, and the sampled IDs, so a second run on the same export picks the same sample.
2. **Check.** Run every check in the table on every sampled record. Mark each remaining field `needs human check` or `empty`. The step is done when every field of every sampled record carries one of `pass`, `fail`, `needs human check`, or `empty`, and every `fail` quotes its value.
3. **Score.** Score = passed checks divided by checked checks (pass plus fail). Report the score per field and overall, against the team bar, as PASS or FAIL. The step is done when the overall number and the bar sit side by side.
4. **Trace.** For each fail, name the likely source, labeled as a hypothesis:
   - A detected field, a format error, or a contact link error traces to the record's `source`. When that source is `manual` or `form`, the enrichment tool behind a detected value is a gap.
   - A confirmed-field error traces to manual confirmation, whatever the record's `source` says: a person wrote it.
   - A duplicate pair counts once, against the record a merge would remove: the one with no owner and no activity. When neither fits, name both sources and say so.

   Tally errors by source as a count and as a rate (errors divided by checked fields from that source), and name the source with the most errors. The step is done when every fail sits in exactly one source's tally.
5. **Propose.** Write one source-level fix per error pattern: the source, the pattern, the error IDs it would prevent, and the change to that source's process (for example, match on domain before creating a company). Where a single record must change, add a row to a proposal file. A row's new value comes from a file or is `(blank)`. A change that is not a field change (a merge) or needs a value no file holds (a confirmation date) goes under Owner actions with its gap. The step is done when every fail maps to a source fix, a proposal row, or an owner action.
6. **Write and stop.** Write `brain/audits/<today>-accuracy.md` in the format below and, when step 5 produced rows, `brain/proposals/<today>-data-accuracy-audit-<short-topic>.md` in the format in `brain/proposals/README.md` with `status: proposed`. When either file already exists, stop and tell the person. Then show the person the score, the top source, and the fixes. The run is done when the files exist and every error in them cites evidence.

## Write boundary

The skill writes only new files in `brain/audits/` and `brain/proposals/`. The export and the CRM stay exactly as they were read. A person approves every proposal and makes every change.

## Audit file format

```markdown
---
skill: data-accuracy-audit
audited_at: <YYYY-MM-DD>
export: <file paths, or the live CRM read>
settings: <sample sizes, pass bar, revenue range, revenue tolerance>
score: <overall %>
result: PASS | FAIL
---

## Sample
<method, N, n, k per object; "audited all N records" when N was n or fewer; sampled IDs>

## Results by field
| Object | Field | Pass | Fail | Needs human check | Empty | Score |

## Errors
| # | Object | Record ID | Field | Value | Check failed | Likely source (hypothesis) |

## Errors by source
| Source | Errors | Checked fields | Error rate |
Most errors: <source>, <count>.

## Proposed source fixes
- <source>: <pattern> (errors #<n>, #<n>). Fix: <process change>.

## Owner actions
- <record ID>: <what a person must do> (gap: <what no file states>)

## Needs human check
- <record ID> <field>: <value>

## Gaps
- <missing fact> (needed by: <check or step>)
```
