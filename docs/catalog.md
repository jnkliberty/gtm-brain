# Skill catalog

This catalog describes the skills in this checkout. Open a skill's linked instructions before use; the inputs below are a selection guide.
Every skill preserves evidence and gaps. Drafts and proposals need human review. No skill sends a message or changes a CRM.

## Release status

**Identify this checkout by its Git commit.** The [plugin manifest](../.claude-plugin/plugin.json) retains starter version `0.3.0`.
The version number alone does not distinguish the starter from this checkout.

| Snapshot | Identity | Availability |
| --- | --- | --- |
| Starter | Commit `3931f0d`, manifest `0.3.0` | Contains the skills marked Starter below. Publication of a specific package is not verified here. |
| Follow-through base | Commit `5e8065b`, manifest `0.3.0` | Adds Follow-through and its signal-record boundaries. Included in this checkout. |
| Audit changes | Changes after `5e8065b`; see this file's Git history | Adds supplied-reply handling and this catalog. No new package version is assigned. |

**Starter** means the skill exists in the starter snapshot and this checkout. It does not mean every connector or agent has been verified.
**Current checkout** means the capability exists in these files beyond the starter snapshot. Check the installed catalog and Git commit; the unchanged manifest version does not prove an installation has these modes.

The supplied-reply mode and routing passed 11 fictional Codex cases, including signal and post-call regressions. Independent review found one conflicting privacy instruction; it was corrected and the routing case passed again. A second finding was rejected because step 4b exists in the full routing skill.
Claude, browser-chat, live inbox, and private-brain integration for that mode remain unverified.
Follow-through's saved review record is summarized in the [README](../README.md#after-a-call). Claude and browser-chat behavior remain unverified.
The starter uses local CSV exports. Live CRM connections need a separate activation plan.
Content skills need no API key; optional engines and Jev use the environment keys described in the [README](../README.md#content-engineering-data-and-keys).

## Choose a skill

### Setup and sales decisions

| Skill | Job | Main inputs | Result | Availability |
| --- | --- | --- | --- | --- |
| [start-here](../skills/start-here/SKILL.md) | Choose the skill for a plain request. | Your task and any missing context. | One suggested skill, or an explanation that none fits. Does not execute the selected workflow. | Starter; supplied-reply routing in current checkout |
| [brain-setup](../skills/brain-setup/SKILL.md) | Replace the invented team rules. | Your answers about customers, stages, plays, and sources. | Proposed ICP, stages, plays, and source map; writes only approved files. | Starter |
| [account-handoff](../skills/account-handoff/SKILL.md) | Decide what sales should do with a signal or an existing conversation reply. | Signal mode: account, CRM export, interpreted signal, rules, and past decisions. Reply mode: current reply, relevant conversation, company context, and explicit owner evidence. | Signal decision or recorded verdict. Reply mode returns intent, evidence, owner, proposed action, gaps, and an optional draft in chat only. | Starter signal mode; supplied-reply mode in current checkout, tested with fictional Codex cases |
| [signal-sweep](../skills/signal-sweep/SKILL.md) | Decide all new signals in one run. | Signals, past signal decisions, and account-handoff inputs. | Signal decisions and a short list of accounts that need a person. | Starter; Follow-through exclusions in current checkout |
| [follow-through](../skills/follow-through/SKILL.md) | Turn a sales call into a supported follow-up. | Authorized notes or transcript, company context, and prior feedback when available. | Recap, actions, one customer draft, evidence, and repair notes; can retain a human verdict. | Current checkout; chat only unless privacy and save authority are confirmed |

### CRM quality and records

All CRM changes remain proposals. The CSV files live under `brain/crm-export/`; each skill names its rules and source checks.

| Skill | Job | Main inputs | Result | Availability |
| --- | --- | --- | --- | --- |
| [icp-filter-calibration](../skills/icp-filter-calibration/SKILL.md) | Check whether an ICP filter selects the intended accounts. | ICP, target range, company export, field rules, and any prior filter. | Filter, match counts, duplicate and ambiguous records, gaps, and a calibration recommendation. | Starter; CSV route |
| [data-accuracy-audit](../skills/data-accuracy-audit/SKILL.md) | Check the accuracy of CRM fields. | Company and contact exports, field rules, column definitions, and audit settings. | Sampled audit, scores for checked fields, errors by source, and proposed source fixes. | Starter; CSV route |
| [crm-field-provenance](../skills/crm-field-provenance/SKILL.md) | Check machine values against confirmed human values. | Company and contact exports, field rules, and a change proposal for the review branch. | Proposal review or export audit; never approves the proposal. | Starter; CSV route |
| [account-build](../skills/account-build/SKILL.md) | Match and screen account candidates before creation. | Account candidates, company export, ICP, tiers, field rules, and proposal rules. | Cited create proposals plus matched, skipped, and escalated accounts. | Starter; CSV route |
| [tiered-contact-build](../skills/tiered-contact-build/SKILL.md) | Select an opening set of contacts by account tier. | Company and contact exports, contact candidates, ICP, tiers, and contact rules. | Verified contact proposals, exclusions, and shortfalls. | Starter; CSV route |
| [contact-retention-review](../skills/contact-retention-review/SKILL.md) | Decide which contacts need review for retention. | Company and contact exports, ICP, contact rules, and optional move evidence. | Keep, restorable archive, hold, or duplicate-merge proposals with evidence. | Starter; CSV route |
| [contact-move-routing](../skills/contact-move-routing/SKILL.md) | Verify job changes and route a proposed follow-up. | As-of date, companies, contacts, move evidence, rules, and existing task proposals. | One classification per person and proposed owner tasks without duplicate tasks. | Starter; CSV route |
| [call-intel-to-themes](../skills/call-intel-to-themes/SKILL.md) | Find supported internal pain themes from calls. | Private call excerpts, company domains, call rules, and field rules. | Internal theme proposal with facts, hypotheses, conflicts, and gaps. | Starter; local evidence |
| [crm-maintenance-runbook](../skills/crm-maintenance-runbook/SKILL.md) | Review which maintenance checks need attention. | Runbook, maintenance history, and local evidence. | Current, due, overdue, or blocked checks with dated owner follow-ups. Starts no schedule. | Starter; local evidence |

### Content and AI answers

These skills use the shared rules in [brain/search/README.md](../brain/search/README.md).
They write proposals, not published pages. Missing or stale inputs remain visible gaps.

| Skill | Job | Main inputs | Result | Availability |
| --- | --- | --- | --- | --- |
| [objections-to-questions](../skills/objections-to-questions/SKILL.md) | Turn buyer objections into ranked questions. | Call themes, excerpts, company domains, ICP, question rules, and optional reviews or supplied text. | Ranked question proposal with quoted sources. Leaves the approved question list unchanged. | Starter; no key required |
| [cited-brief](../skills/cited-brief/SKILL.md) | Plan one supported page or check its draft. | Approved questions and facts, publishable proof, source rules, voice, writing rules, and a page or draft. | Cited brief or draft-check proposal with a check report. | Starter; optional Jev judgments |
| [buyer-prompt-panel](../skills/buyer-prompt-panel/SKILL.md) | Check whether AI answers name the company. | Approved questions, own domain, source rules, and API, tracker, or pasted answers. | Prompt panel and proposal with mentions, citations, and evidence. | Starter; optional engine APIs |
| [mention-to-deal-ledger](../skills/mention-to-deal-ledger/SKILL.md) | Compare AI mentions, traffic, and deals for one month. | Panel runs, analytics export, deals export, company domains, approved own domain, and source rules. | Monthly ledger with unknown attribution and missing inputs stated. | Starter; local exports |
| [brand-facts-audit](../skills/brand-facts-audit/SKILL.md) | Find wrong or unsupported company claims in AI answers. | Stored answers and approved brand facts. | Quoted mismatches and unsupported claims for human review. | Starter; local answers |
| [competitor-comparison-pages](../skills/competitor-comparison-pages/SKILL.md) | Plan a comparison or alternatives page. | Approved competitor and company facts, publishable proof, approved question, page type, and named owner. | Page proposal with dated prices, competitor wins, evidence, and review cadence. | Starter; approved facts required |

## Structural verification

Reuse the existing check from the repository root:

```bash
python3 scripts/graph_check.py
```

On October 28, 2026, the graph check returned `graph ok`. A local comparison found 20 catalog rows for 20 skill entrypoints.
The README and catalog local link targets also resolved. These checks do not verify model behavior.

The graph check verifies links under `brain/` and `skills/`, and reachability from `brain/index.md`.
It does not verify this catalog's completeness, links in `docs/`, package publication, or model behavior.
Before a release, compare these rows with `skills/*/SKILL.md`, check the manifest, and run the relevant behavior evaluations.
A structural pass does not establish that the skills produce correct decisions.
