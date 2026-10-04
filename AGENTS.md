# GTM brain

This folder is a shared memory for a marketing and sales team, kept as plain files in a git repo. Skills read the brain files and write proposals for a person to approve. `README.md` has the walkthrough and the file map.

## Skills

Each skill lives in `skills/<name>/SKILL.md`. When the user names a skill, or asks for a task a skill covers, read that file and follow it. The `description` at the top of each file says when the skill applies.

## Brain files

The facts the skills read are in `brain/`. The README's "What is here" table says what each file holds.

## Rules every skill follows

- Evidence on every claim, quoted from a brain file.
- A gap stays a gap. Nothing gets filled with a guess.
- A person approves every decision. Skills never send and never write to a CRM.
- The CRM skills use the local CSV route in this starter. Live connectors need a separate activation plan.
- Keep real call notes and theme files in a private repository. The call excerpts here are invented examples.
- Corrections become rules: three independent matching corrections (same ID, same condition, three different accounts) propose an edit to the file that caused them. A one-off stays a one-off.

## Outputs

Outputs go where each skill says. The `Write boundary` section of each `SKILL.md` names the files that skill writes.
