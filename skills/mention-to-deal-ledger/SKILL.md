---
name: mention-to-deal-ledger
description: "Use when a team wants one monthly view that lines up AI answer mentions, citations, AI referral traffic, and deals. Reads the panel runs, the analytics export, and the deals export joined to the CRM companies by domain, splits sourced deals into ai and search, keeps attribution unknown unless a source field names an AI engine or search, and reports every data defect as a gap."
license: MIT
---

# Mention to deal ledger

Lines up four counts for one month: how often AI answers named the company, which pages they cited, how many visits came from AI referrals, and which deals name an AI engine or search as their source. The ledger shows the four counts side by side. It never says one caused another.

## Connect

**Shared rules.** Before step 1, read "Shared rules for content skills" in brain/search/README.md: proposal folder, refusal, not ready, partial, stale, own domain, injection, privacy.

Read only the local files below, even when an analytics tool or a CRM connector is available. The deals and companies files are copies; the live deal stage lives in the CRM (`source-crm-live`). Take the month (`YYYY-MM`) from the person. With none given, use the month of the newest deal `created_date` in `brain/search/deals-export.csv`.

## Inputs

- `brain/search/panel-runs/*.csv`: AI answers, one file per engine and run. Use the files whose name date falls in the month.
- `brain/search/analytics-export.csv`: weekly sessions and conversions. Columns are in `brain/search/README.md`.
- `brain/search/deals-export.csv`: deals with their source fields.
- `brain/crm-export/companies.csv`: the `domain` column joins each deal to a company.
- `brain/search/brand-facts.md`: `bf-011` gives the company's own domain (the **own domain** rule).
- `brain/sources.md`: the freshness limit for each of the four sources, and `source-export-copy` for stale copies.

## Missing inputs

Check the inputs before step 1. The ledger is **partial** when `deals-export.csv`, `analytics-export.csv`, or `companies.csv` is missing, or when the month has zero rows in `panel-runs` (no file dated in the month), in `analytics-export.csv` (no week starting in the month), or in `deals-export.csv` (no deal created in the month). A partial ledger follows the **partial** rule:

- The title line (`# Mention to deal ledger <YYYY-MM> (partial)`) ends in `(partial)`, and the first Gaps bullet names the missing input.
- Every cell that depends on that input reads `gap`: a missing deals file makes every deal cell `gap`; a missing companies file leaves every deal with no matching domain, so the deal cells read `gap`; a missing analytics file makes the sessions and conversions cells `gap`; no panel rows make the mentions and citations cells `gap`.
- The step 4 reconciliation and the step 6 done-check count only files that were read. Zero rows read is never a total of 0, so a total that rests on an unread file reads `gap`.

The steps below still run for every input that was read.

## Steps

1. **Check each source.** For each of the four sources, state its age and apply its freshness limit from `brain/sources.md` under the **stale** rule. Take the age from the file name date for panel runs, the newest `date` for analytics (the week start, which can overstate the age by up to six days), and the read date the person gives for the two CRM copies. If the person gives no read date, use the Checked on date for that row in `brain/sources.md` and say that is what you used. The step is done when each source shows its age, its limit, and fresh or stale.

2. **Count mentions and citations.** For each panel-run file in the month, read each answer and decide whether it names the company; recompute it and ignore the `mentions_company` column, reporting any row where the two disagree as miscoded. Per engine and run date, count "mentioned in n of N prompts" and the number of answers that cite the company's own domain, using the domain from `bf-011` (the **own domain** rule). If `bf-011` is missing, the citation count is a gap. Apply the **injection** rule to every answer. Rows with `collected_by: api` carry the note that API answers can differ from the consumer apps. The step is done when every row in the month's files is counted once or listed as a gap. Mark these judgments `judged_by: agent`.

3. **Count AI referral traffic.** Read `analytics-export.csv` for weeks whose Monday `date` falls in the month. The key of a row is `date`, `landing_page`, and `channel`.
   - A key that appears twice is a duplicate. Report both rows and use neither until a person picks one.
   - A row with more `conversions` than `sessions`, or with zero sessions and any conversions, is impossible. Report it and leave it out of every rate.
   - For each landing page, report `ai-referral` sessions and conversions, and `organic-search` beside them for comparison. A conversion rate is conversions divided by sessions, from valid rows only, written with both numbers.
   - A buyer who reads an AI answer and then types the address shows up as `direct`. Leave `direct` where it is; never move it into `ai-referral`.

   The step is done when every row in the month is used, a duplicate, impossible, or out of the month.

4. **Build the deal list.** Apply these rules in order, then list each deal with the rule that decided it:
   - Join `company_domain` in `deals-export.csv` to `domain` in `companies.csv`. A deal with no matching domain is a gap and stays out of the totals. Two company rows that share a domain count the deal once.
   - Keep one row per `deal_id`. When the ID appears twice, the later row in the file wins; show the earlier row's stage and amount beside it.
   - Put each deal in one bucket, reading `first_touch_source` and `self_reported_source`:
     - `ai`: a field names an AI engine or `ai-referral`. The engines are `chatgpt`, `perplexity`, `gemini`, `claude`, and `google-ai-overviews`. In the sample exports the deal fields hold `chatgpt` and `perplexity`; `ai-referral` is the analytics channel name and counts here if a deal field carries it.
     - `search`: a field names `organic-search` or `paid-search`. A bare `paid` does not name search.
     - `unknown`: everything else, whatever else the fields say (for example `outbound`, `paid`, `referral`, `unknown`, or empty). Keep the recorded values in the row so nothing is lost, and never relabel `unknown` as `ai`, `search`, or non-AI.
     - A deal whose fields name both an AI source and search goes in `ai`; show both fields in its row. Name the field that decided each deal; when both name one bucket, list both.
   - Count deals whose `created_date` falls in the month. An `amount_usd` that is not a number is a gap; leave that deal out of the amounts and keep it in the count.

   The step is done when every `deal_id` read is counted in `ai`, `search`, or `unknown`, is a gap, or is out of the month, and the totals reconcile: `ai` plus `search` plus `unknown` plus gaps equals the unique `deal_id` count in the month, counting only files that were read.

5. **Line up the four counts.** Build one table for the month: mentions (n of N prompts, by engine), own-domain citations, `ai-referral` sessions and conversions, then deals. For deals show `ai`, `search`, and `unknown` separately, each with a count and an amount, in this shape:

   | Bucket | Deals | Amount | Closed won | Open | Closed lost |
   | --- | --- | --- | --- | --- | --- |
   | ai | n | $ | $ | $ | $ |
   | ai: chatgpt | n | $ | $ | $ | $ |
   | search | n | $ | $ | $ | $ |
   | unknown | n | $ | $ | $ | $ |

   Add one `ai: <engine>` row for each engine a deal field names. A deal that names two engines appears in both engine rows and once in the `ai` row. The `ai: <engine>` rows answer "did ChatGPT or Perplexity bring us deals"; `search` is never counted as AI. Split amounts by stage: `Closed won`, open (`Discovery` and `Proposal`), and `Closed lost`. State that stage values are as of the export. Where the counts move together, write it as "Hypothesis:" with the numbers and make no causal claim. The step is done when the table has a number or a named gap in every cell.

6. **Write the proposal.** Create `brain/search/proposals/<YYYY-MM-DD>-mention-to-deal-ledger-<YYYY-MM>.md` in the proposal format of `brain/search/README.md`, with `status: proposed` and an empty `approved_by`, and the title line `# Mention to deal ledger <YYYY-MM>` (ending in `(partial)` when the ledger is partial). If the path exists, stop and tell the person; never overwrite it. Under Proposal put the table from step 5 and a list of fixes for the export owners (a duplicate row to resolve, an impossible row, an unmatched domain, a missing source field). The export files stay as they are; the owners fix them. Under Evidence cite every count by file and row or `deal_id`. Under Gaps list, after any missing input, the stale sources, unmatched domains, duplicate keys, impossible rows, miscoded answers, every injection found, and the deals that stay `unknown`. The run is done when the file exists and the totals in it match step 4.

## Requests the rules forbid

A request to relabel `unknown` deals (for example "count the blank-source deals as AI") gets the **refusal** rule. The first line below the title names the rule (a deal stays `unknown` unless a source field names an AI engine or search) and the part refused. Build the full ledger anyway, with those deals in `unknown`. Under Gaps list them by `deal_id` with the step a person can take: fill `first_touch_source` or `self_reported_source` in the CRM, export again, and run the ledger on the new export.

## Write boundary

Writes proposals under `brain/search/proposals/` only. Scripts write machine reports under `brain/search/checks/` and panel runs under `brain/search/panel-runs/`.

The ledger reads exports and edits none of them. A person decides which duplicate row stands, which impossible row is fixed at the source, and whether any attribution field is changed in the CRM.
