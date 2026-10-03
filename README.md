# GTM brain

A shared memory for a marketing and sales team, kept as plain files in your own git repo.

MIT starter. The CRM examples use invented CSV data and create proposals for a person to review.

## Five-minute walkthrough

1. Install the skills as a plugin, then clone this repository and open it in Claude Code. The plugin holds the skills; the clone holds the brain files they read.

   ```bash
   claude plugin marketplace add jnkliberty/gtm-brain
   claude plugin install gtm-brain@gtm-brain
   git clone https://github.com/jnkliberty/gtm-brain.git
   cd gtm-brain
   claude
   ```

2. Ask: `Run account-handoff for Northwind Robotics on the 2026-09-24 signal.` The skill reads `brain/accounts/northwind-robotics.md`, the account's row in `brain/crm-export/companies.csv`, the dated signal, and the rules in `brain/stages.md`, `brain/plays.md`, and `brain/sources.md`.
3. Read the proposed file in `brain/decisions/`. Check that the decision and draft cite the source lines. The example has no verified email, so the proposal must keep that gap open.
4. Approve, edit, or reject the proposal. The skill records your verdict; an edit or rejection also goes in `brain/corrections.md`. Nothing sends or changes a CRM.

Northwind Robotics, its activity, and the signal are invented. Replace the sample records with your own private data only in a private copy of this repo.

## Make it yours

Do this in a private copy of the repo. Your answers and records are your company's data.

1. Ask: `Run brain-setup.` It interviews you about your ICP, stages, plays, and where each fact lives, one file at a time. It shows each proposed file and writes only the ones you approve. A question you skip stays a visible gap.
2. Export your CRM in the `brain/crm-export/README.md` format, add one account file and one signal, and run `account-handoff` on them. Setup is done when that decision file cites your own records, not Northwind's.

## What is here

| Path | What it holds |
| --- | --- |
| `brain/icp.md` | Who you sell to, and who fails the cut |
| `brain/stages.md` | Lifecycle stages, who owns each, and the handoff rules |
| `brain/plays.md` | Your plays, their triggers, and the draft rules |
| `brain/accounts/` | One file per account: what marketing and sales know |
| `brain/signals/` | Signals on accounts, interpreted by `signal-interpreter` |
| `brain/decisions/` | Proposed decisions, each waiting for a person's verdict |
| `brain/corrections.md` | Every edit or rejection, so repeated mistakes become rule changes |
| `brain/sources.md` | Where each kind of fact lives, and which place wins when two disagree |
| `skills/account-handoff/` | Turns a marketing signal into a sales decision |
| `skills/brain-setup/` | Interviews your team and proposes your own ICP, stages, plays, and source map |
| `.claude-plugin/` | Plugin and marketplace manifests, so every skill installs with one command |
| `brain/crm-export/` | Invented account, contact, candidate, and move-evidence CSVs |
| `brain/call-rules.md`, `brain/calls/` | Private synthetic call excerpts and theme rules |
| `brain/runbook.md`, `brain/maintenance/` | Maintenance checks, history, and synthetic evidence |
| `skills/icp-filter-calibration/`, `skills/data-accuracy-audit/`, `skills/crm-field-provenance/` | Read-only CRM checks |
| `skills/account-build/`, `skills/tiered-contact-build/`, `skills/contact-retention-review/` | Record-building and retention proposals |
| `skills/contact-move-routing/`, `skills/call-intel-to-themes/`, `skills/crm-maintenance-runbook/` | Move, call, and maintenance reviews |

## Rules every skill follows

- Evidence on every claim, quoted from a brain file.
- A gap stays a gap. Nothing gets filled with a guess.
- A person approves every decision. Skills never send and never write to a CRM.
- The CRM skills use the local CSV route in this starter. Live connectors need a separate activation plan.
- Keep real call notes and theme files in a private repository. The call excerpts here are invented examples.
- Corrections become rules: three matching corrections propose an edit to the file that caused them.

## License

MIT. See [LICENSE](./LICENSE). `signal-interpreter` is by Swan ([swan-gtm/gtm-skills](https://github.com/swan-gtm/gtm-skills), MIT).
