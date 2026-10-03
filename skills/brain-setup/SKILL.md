---
name: brain-setup
description: "Use when a team adopts this brain and needs its own ICP, stages, plays, and source map in place of the invented examples. Interviews the team one file at a time, then proposes brain/icp.md, brain/stages.md, brain/plays.md, and brain/sources.md in the team's words for a person to approve. Also use to redo one of those files when the team's process changes."
license: MIT
---

# Brain setup

Replaces the invented examples in the four policy files with the team's own policy. The skill owns the interview and the file structure. The team owns every value. The other skills find their rules by ID and heading, so the structure stays and the content changes.

## The team's words

**The team's words** is the leading word. Every value in a proposed file restates an answer the person gave in this interview.

- An **answer** is what the person said, recorded word for word under its question ID.
- `keep` is a valid answer: that part of the current file stays as written.
- An **unanswered** question is a gap. The proposed file holds `GAP: <question ID>` where the value would go. An example value never fills a gap.
- A value from anywhere else (the example files, a website, a guess) is not the team's words.

## What stays fixed

The other skills depend on these. Keep them exactly; the team changes only what they hold.

- `brain/icp.md`: one line per in or out criterion, and the target range as two numbers.
- `brain/stages.md`: the four handoff rules, in this order, with these IDs and decisions: `rule-skip` (skip), `rule-route-to-owner` (route to owner), `rule-act-now` (act now), `rule-nurture` (nurture). `rule-skip` and `rule-nurture` keep their conditions as written. `rule-act-now` always keeps two conditions: the signal's `relevanceVerdict` is `relevant`, and the current signal matches one play's trigger in `brain/plays.md`. The team sets the stage names (`q-stages`), the conditions of `rule-route-to-owner` (`q-sales-owned`), and the other conditions of `rule-act-now` (`q-act-now`).
- `brain/plays.md`: each play is a `##` heading that is its ID (lowercase words joined by hyphens) with **Trigger**, **Angle**, and **Offer** bullets, most important first. The six draft rule IDs stay: `draft-length`, `draft-unique-fact`, `draft-ask`, `draft-public-only`, `draft-plain`, `draft-recipient`.
- `brain/sources.md`: the sections Surfaces, Where to look, and Conflict order. The six source rules stay as written, in order.

## Questions

Ask one question at a time. When it helps, show what the current file says as an example.

**`brain/icp.md`**
- `q-icp-in`: Which companies do you sell to? Segment, size range, industry, and anything about their team or tools.
- `q-icp-out`: Which companies fail the cut, even when they look close?
- `q-icp-range`: How many accounts can your team actually work? Give a low and a high number.

**`brain/stages.md`**
- `q-stages`: List your lifecycle stages in order. For each one: who owns it, marketing or sales, and what moves an account into it.
- `q-sales-owned`: Which stages mean sales already owns the account?
- `q-act-now`: When should marketing hand an account to sales right away? Name the signal strength and timing you need.

**`brain/plays.md`**
- `q-plays`: List your plays, most important first. For each one: what triggers it, the angle, and the offer in the words you would send.
- `q-draft-rules`: For each draft rule in the current file, keep it or say what to change.

**`brain/sources.md`**
- `q-systems`: Which CRM, call recorder, enrichment vendor, and chat tool do you use?
- `q-owners`: For each row in "Where to look", where does the truth live, and who owns it?
- `q-export`: How do skills read your CRM: an export in the `brain/crm-export/README.md` format? On what date was it taken?

## Steps

1. **Read.** Read the four files and `brain/corrections.md`. When the person asks to redo one file, start a new record at `brain/setup/<today's date>-<that file's name without .md>.md` that lists only that file. Otherwise, when an earlier record still lists a file as `not started` or `proposed`, continue that record. Otherwise, start a new record at `brain/setup/<today's date>-setup.md` that lists all four files. Use the format below. A setup record is never overwritten: when the name is taken, stop and tell the person. The step is done when the record lists each file in scope with its status.
2. **Interview one file.** Take the next file in the record that is `not started` or `proposed`, in the order icp, stages, plays, sources. Approved and rejected files are done. A `proposed` file already has its answers: go to step 3 and show the proposal again. Otherwise ask its questions and record each answer. The step is done when every question for that file has an answer, `keep`, or `unanswered`.
3. **Propose that file.** Write the full proposed text under the file's heading in the record, with `status: proposed`. In `brain/sources.md`, a row the person answered gets today's date under "Last checked". Under the proposal, list follow-ups: each line in another `brain/` file or skill that names a stage, play ID, or system the proposal removes or renames, each line of `brain/corrections.md` that points at a removed ID, and, when `brain/icp.md` changes, each ICP line in `brain/accounts/` for the person to recheck. Show the person the proposed text and the follow-ups. The step is done when every value restates an answer, comes from a kept part, is a fixed item, or is a `GAP:` line.
4. **Write on yes.** When the person says yes to that exact text, write it to the file and set its status to `approved` with the date. When they give a change, record it as a new answer and return to step 3. When they say no, set `rejected` and leave the file as it was. Then return to step 2 for the next file. The run is done when every file in the record is approved or rejected, or the person stops; the record shows where to pick up.

## Write boundary

The skill writes files in `brain/setup/` and, only after a yes to the exact text, the four files above. The person makes the follow-up edits. Sample records (the Northwind account, its signal, the CRM export) stay until the person replaces them.

## Setup record format

```markdown
---
started_at: <YYYY-MM-DD>
---

## Answers
- q-icp-in: "<answer, word for word>"
- q-icp-out: keep
- q-icp-range: unanswered

## brain/icp.md
status: not started | proposed | approved <YYYY-MM-DD> | rejected <YYYY-MM-DD>

<the full proposed file>

Follow-ups:
- <file>:<line> names "<old value>", which this proposal removes or renames

## brain/stages.md
status: not started
```
