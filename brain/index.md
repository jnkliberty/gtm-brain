---
description: "Entry point to the brain. Lists every brain file by task, says when to open each one, and names the skills that read it. Read it first, then open only what the task needs."
---

# Brain index

The brain holds a marketing and sales team's facts as plain files. It covers rules for accounts, contacts, and CRM data; call notes and themes; and the approved facts behind content. Read this file first. Then search `brain/` for `^description:` to scan every file's one-line description, and open only the 1 to 3 files the task needs. CSV and text files have no description, so read the README or rule file beside them.

## Accounts, contacts, and outbound

- Open [icp.md](icp.md) to judge whether an account fits. Read by `account-build`, `brain-setup`, `contact-retention-review`, `icp-filter-calibration`, `objections-to-questions`, and `tiered-contact-build`.
- Open [stages.md](stages.md) to decide what happens to a signal or what a handoff must name. Read by `account-handoff` and `brain-setup`; `signal-sweep` applies it by running `account-handoff`.
- Open [plays.md](plays.md) to pick a play or write a first-touch draft. Read by `account-handoff` and `brain-setup`.
- Open [corrections.md](corrections.md) before you decide an account, to see which rules people already edited or rejected. Read by `account-handoff` and `brain-setup`; `account-handoff` also adds a line when a person edits or rejects a decision.
- Open [tiers.md](tiers.md) to set an account's tier from its revenue. Read by `account-build` and `tiered-contact-build`.
- Open [contact-rules.md](contact-rules.md) to decide how many contacts an account holds, which to keep, and when a job change counts as a move. Read by `contact-move-routing`, `contact-retention-review`, and `tiered-contact-build`.
- Open [accounts/](accounts/) for what marketing and sales know about one account. Each file is named `<company>.md`, such as `northwind-robotics.md`. Read by `account-handoff`, `brain-setup`, and `signal-sweep`.
- Open [signals/](signals/) for the interpreted signals on accounts, one file each, with the date first in the name, such as `2026-09-24-northwind-founding-gtm-engineer.md`. Read by `account-handoff` and `signal-sweep`.
- Open [decisions/](decisions/) for proposed decisions that wait on a person's verdict. Each file is named `<date>-<company>-<signal file name>.md`. `account-handoff` writes them and reads earlier ones to count the budget; `signal-sweep` reads them to find signals with no decision.

## CRM upkeep

- Open [sources.md](sources.md) before you propose, audit, or quote any CRM value. It says where each fact lives, which place wins when two disagree, and how many days a copy stays fresh. Read by `account-build`, `account-handoff`, `brain-setup`, `buyer-prompt-panel`, `call-intel-to-themes`, `cited-brief`, `contact-move-routing`, `contact-retention-review`, `crm-field-provenance`, `data-accuracy-audit`, `icp-filter-calibration`, `mention-to-deal-ledger`, `objections-to-questions`, and `tiered-contact-build`.
- Open [field-rules.md](field-rules.md) when a record holds both an enrichment value and a person-confirmed value for one field. Read by `account-build`, `call-intel-to-themes`, `contact-move-routing`, `crm-field-provenance`, `data-accuracy-audit`, `icp-filter-calibration`, and `tiered-contact-build`.
- Open [crm-export/README.md](crm-export/README.md) for the column meanings before you read a CSV in [crm-export/](crm-export/), the dated CRM snapshot with one CSV per record type. Read by `account-build`, `account-handoff`, `brain-setup`, `call-intel-to-themes`, `contact-move-routing`, `contact-retention-review`, `crm-field-provenance`, `data-accuracy-audit`, `icp-filter-calibration`, `mention-to-deal-ledger`, `objections-to-questions`, and `tiered-contact-build`.
- Open [proposals/README.md](proposals/README.md) for the row format before you write or review a CRM change. Files in [proposals/](proposals/) are named `<YYYY-MM-DD>-<skill>-<short-topic>.md`. Read by `account-build`, `contact-move-routing`, `contact-retention-review`, `crm-field-provenance`, `crm-maintenance-runbook`, `data-accuracy-audit`, `icp-filter-calibration`, and `tiered-contact-build`.
- Open [runbook.md](runbook.md) when you check whether a maintenance review is current, due, overdue, or blocked. Read by `crm-maintenance-runbook`.
- Open [maintenance/](maintenance/) for the completion history (`history.csv`), the evidence files in `evidence/`, and the dated reviews named `<as-of-date>-review-<short-topic>.md`. `crm-maintenance-runbook` reads the history and evidence and writes the reviews.

## Call intelligence

- Open [call-rules.md](call-rules.md) before you read call notes or write a theme. It says when an excerpt counts as confirmed and when a pain recurs. Read by `call-intel-to-themes` and `objections-to-questions`.
- Open [calls/call-notes.csv](calls/call-notes.csv) for call excerpts, one quote per row. Read by `call-intel-to-themes`, `objections-to-questions`, and `cited-brief`.
- Open [themes/](themes/) for the recurring pains that call notes support, one file per theme, named `<YYYY-MM-DD>-<short-topic>.md`. `call-intel-to-themes` writes them; `objections-to-questions` and `cited-brief` read them.

## Content engineering

- Open [search/README.md](search/README.md) first for any content task. It is the map of [search/](search/): what each file holds, its columns, and the rules every content skill follows. Scan the `description` of each file in [search/](search/) to choose which to open. Read by `objections-to-questions`, `cited-brief`, `buyer-prompt-panel`, `mention-to-deal-ledger`, `brand-facts-audit`, and `competitor-comparison-pages`; `start-here` reads its privacy rule.
- Open [voice.md](voice.md) when you write or check a draft. `cited-brief` reads it, and `scripts/content_checks.py` runs its rules.
- Open [proof.md](proof.md) when a page cites a customer result. Read by `cited-brief` and `competitor-comparison-pages`.
- Check [sources.md](sources.md) for how many days each of these sources stays fresh.

## Gaps

- `signal-interpreter` produces the files in [signals/](signals/), but `skills/` has no folder for it and the README credits swan-gtm/gtm-skills. [account-handoff](../skills/account-handoff/SKILL.md) expects its output format.
- Skills create these folders on their first write, so they are missing today and have no link: `audits/` (`data-accuracy-audit`), `calibration/` and `filters.md` (`icp-filter-calibration`), `moves/` (`contact-move-routing`), `provenance/` (`crm-field-provenance`), `setup/` (`brain-setup`), `search/proposals/` and `search/checks/` (the content skills and scripts).
