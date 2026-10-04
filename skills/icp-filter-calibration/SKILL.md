---
name: icp-filter-calibration
description: "Use when a written ICP needs to become a filter a CRM export can run, or when the number of accounts that match the ICP needs checking against the team's target range. Writes the filter to brain/filters.md, runs it, and records the match count, duplicates, ambiguous records, gaps, and whether to tighten or loosen. Also use after someone edits brain/icp.md, to recalibrate."
license: MIT
---

# ICP filter calibration

Turns the plain-language ICP in `brain/icp.md` into a filter with one row per criterion, runs it on the team's companies, and tells the person whether the match count fits the range the team can work. The skill owns the process. The ICP stays in the team's words, so a team changes who it sells to by editing `brain/icp.md`, never this file.

## Evidence, repeatability, and gaps

**Repeatable** is the leading word. A criterion is repeatable when its written definition gives one answer for every record: two people applying it to the same row get the same result.

- A **match** is a record that passes every checkable criterion. Cite the value that decided each criterion: `companies.csv <company_id> <column>: <value>`.
- An **ambiguous** record is one where a criterion's definition gives no single answer: the cell is empty or `unknown`, the value is free text the definition does not settle, or the definition reads two ways. An ambiguous record is neither matched nor rejected. It is listed with the criterion and the reason.
- A **gap** is a criterion no export column records. It filters nothing, so the match count is a count before that criterion. A column whose name sounds related but whose meaning in `brain/crm-export/README.md` records something else is still a gap.
- Every criterion quotes the line of `brain/icp.md` it comes from. A rule from any other file is not a criterion.

## Inputs

- `brain/icp.md`: the ICP and the target range.
- `brain/field-rules.md`: detected and confirmed field pairs. Filters follow `rule-confirmed-wins`.
- `brain/crm-export/README.md`: what each column means.
- Company records, from a live CRM or `brain/crm-export/companies.csv` (see Connect).
- `brain/filters.md` and `brain/calibration/`, when they exist: the previous filter and past runs.

## Connect

When a live CRM connection is available (for example a HubSpot, Salesforce, or Attio MCP server or API), read companies from it, read-only. Map each CRM property to the export column with the same meaning in `brain/crm-export/README.md`, and write the mapping into the calibration record. A column with no matching property is empty for every record.

Otherwise ask the person for an export in the `brain/crm-export/README.md` format, or use `brain/crm-export/companies.csv` when they point to it. Wave 1 only reads a CRM. Any CRM change goes to the person as a proposal in the `brain/proposals/README.md` format.

## Source check

Before a step uses a fact or proposes a value or record, find the fact's row in "Where to look" in `brain/sources.md` and apply its Conflict order. Cite the winning source's rule ID and read date. A fact with no row is a gap (`source-unmapped`). A copy older than its "Fresh for" days, counted to the date of the run, is stale. Each company value is a copy (`source-export-copy`) unless a live CRM read supplied it. When records at one domain give different values for a criterion's column with no winner, or the value is stale, the answer is ambiguous with the rule ID as its reason; it is not pass or fail. Such an answer is a data gap, not a wording problem: fixing the source resolves it, so step 4 proposes no `brain/icp.md` wording for it and a criterion is not marked unrepeatable because of it. When source-caused answers alone decide whether the count is in range, step 6 recommends a fresher or reconciled export instead of `tighten` or `loosen`. `rule-confirmed-wins` in `brain/field-rules.md` still picks between a detected and a confirmed value in one record. Never pick one value silently, and keep this ranking in `brain/sources.md`, not here.

## Steps

1. **Read.** Read the inputs and number every line of `brain/icp.md` that puts a company in or out of the ICP as a criterion with an ID (`crit-<short-name>`). When `brain/filters.md` exists, keep its IDs for criteria whose wording is unchanged, so runs compare. The step is done when every in or out line of `brain/icp.md` has an ID, and the target range is read as two numbers or listed as a gap.
2. **Write the filter.** For each criterion, choose the export column whose README meaning records it, then an operator (`equals`, `one-of`, `not-one-of`, `between`, `at-least`, `at-most`, `contains`) and a value. For a detected and confirmed pair, the column reads `<x>_confirmed, else <x>_detected`. Write what qualifies and what does not in plain words. A criterion no column records gets `none` for column, operator, and value, and `no (gap)` under Checkable. The step is done when every criterion has one row and every row either names a column the README defines or is marked a gap.
3. **Run the filter.** Apply every checkable criterion to every record. Each record and criterion pair gets one answer: pass, fail, or ambiguous, with the cell value that decided it. For a paired field, record which field supplied the value. Apply the source check to each value first. The step is done when no pair is left without an answer and every ambiguous answer names why the definition gives no single answer.
4. **Test repeatability.** A criterion is repeatable only when it gave zero ambiguous answers. For each criterion that is not, write the exact wording change to `brain/icp.md` that would give one answer for each of its ambiguous records. The step is done when every criterion is marked repeatable or carries a proposed wording.
5. **Count.** Group the matched records by `domain`; records that share a domain are likely duplicates and count once. Compare the unique count with the target range. State how the ambiguous records could move the count: the count if all of them matched. The step is done when the record count, the unique count, and the range sit side by side with every duplicate group listed.
6. **Recommend.** `in range` when the unique count sits in the range, `tighten` when it is above, `loosen` when it is below. For tighten or loosen, name the one criterion to change and the wording, and cite the records that change would move. When the ambiguous records alone decide whether the count is in range, say so and point at step 4 first. The step is done when the verdict names a criterion or states that none needs to change.
7. **Write and stop.** Rewrite `brain/filters.md` and write `brain/calibration/<today's date>-icp.md` in the formats below. When that calibration file already exists, stop and tell the person; a calibration record is never overwritten. Then show the person the verdict, the ambiguous records, the gaps, and each proposed `brain/icp.md` wording. The run is done when both files exist and every claim in them cites a record, a column, or a quoted ICP line.

## Write boundary

The skill writes `brain/filters.md` and new files in `brain/calibration/`. The export and `brain/icp.md` stay as the person left them: a proposed ICP wording is shown to the person, who makes the edit. Nothing is written to a CRM.

## Filter file format

```markdown
---
icp: brain/icp.md
built_at: <YYYY-MM-DD>
---

| ID | Criterion (brain/icp.md) | Export column | Operator | Value | Qualifies | Does not qualify | Checkable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| crit-<name> | "<quoted line or phrase>" | <column> | <operator> | <value> | <plain words> | <plain words> | yes |
| crit-<name> | "<quoted line or phrase>" | none | none | none | <plain words> | <plain words> | no (gap) |
```

## Calibration record format

```markdown
---
skill: icp-filter-calibration
run_at: <YYYY-MM-DD>
source: <brain/crm-export/companies.csv with its read date, or CRM name (read-only)>
filter: brain/filters.md
target_range: <low> to <high>
matched_records: <n>
matched_unique: <n>
ambiguous_records: <n>
verdict: in range | tighten | loosen
---

## Matched records
| company_id | name | domain | Deciding values |

## Count against the target
<matched records>, <unique after duplicates>, target <range> (brain/icp.md: "<quoted line>"). If every ambiguous record matched: <n>.

## Likely duplicates
| domain | company_ids | Counted as |

## Ambiguous
| company_id | Criterion | Value in export | Why the definition gives no single answer |

## Repeatability
| Criterion | Repeatable | Proposed brain/icp.md wording |

## Gaps
| Criterion | brain/icp.md line | Why no export column records it |

## Recommendation
<in range | tighten | loosen>: <criterion ID and proposed wording, or "no change">, because <reason with records cited>. The person makes any edit to brain/icp.md.

## CRM mapping (live connection only)
| CRM property | Export column |
```
