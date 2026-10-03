---
name: account-handoff
description: "Use when a marketing signal on an account needs a sales decision: act now, nurture, skip, or route to the owner. Reads the account file, the account's row in the CRM export, and a signal already interpreted by signal-interpreter, picks a play, drafts the first touch with evidence on every claim, and logs a proposed decision for a person to approve. Also use to record a person's verdict on a proposed decision."
license: MIT
---

# Account handoff

Turns what marketing knows about an account into a sales decision a person can approve in one read. The skill owns the process. The team's policy lives in the brain files, so a team changes its rules by editing `brain/stages.md`, `brain/plays.md`, and `brain/sources.md`, never this file.

## Evidence, facts, and gaps

**Evidence** is the leading word. Every reason, the play, and the angle cite a brain file and quote the line they rest on.

- A **fact** is something a source states in its own words: the source text quoted in a signal file (for example, the posting) and what an account file records (activity, contacts, stack, stage). Facts may appear in the draft.
- A **hypothesis** is an interpretation: every field the signal interpreter wrote, including `cleanSummary`, `likelyMeaning`, `businessImplication`, `whyNow`, `signalStrength`, and `confidence`. Hypotheses support the decision and stay inside the decision file, labeled as hypotheses. They never appear as claims in the draft.
- A **gap** is anything the decision needs that no file states. A gap is written down as a gap and left open.
- A **copy** is a value recorded in one file whose truth `brain/sources.md` places somewhere else, for example a stage or owner in an account file when the map places live status in the CRM. A copy is cited with the date it was read from its source.

## Inputs

- `brain/accounts/<company>.md`: what the team knows about the account.
- The account's CRM record: the row in `brain/crm-export/companies.csv` whose `company_id` matches the account file's CRM record ID. Its read date is the export's snapshot date in `brain/sources.md`. This starter reads the export only; a live CRM read needs its own activation plan (see `README.md`).
- One interpreted signal in `brain/signals/`, in the `signal-interpreter` output format (`relevanceVerdict`, `signalType`, `cleanSummary`, `likelyMeaning`, `signalStrength`, `confidence`, `whyNow`, `whatNotToAssume`, `openQuestions`).
- `brain/stages.md`: lifecycle stages and the handoff rules, each with an ID.
- `brain/plays.md`: the team's plays in priority order, each with an ID, plus the draft rules.
- `brain/corrections.md`: past verdicts. Read it before deciding.
- `brain/sources.md`: where each kind of fact lives and which place wins when two disagree, each rule with an ID.

## Branch A: decide on a new signal

1. **Read.** Read the seven inputs. Match each fact to its row in "Where to look" in `brain/sources.md`. A fact with no row adds a gap naming the missing row (`source-unmapped`). A copy with no read date adds a gap naming the missing date (`source-export-copy`). Compare the account file's stage and owner with the CRM record. When they disagree, both values are copies, so `source-export-copy` in `brain/sources.md` decides. Use the winning value in every rule, cite it with its read date, and list the disagreement under Gaps with the update you propose to the other copy (`source-fix-copy`). An unresolved field goes under Gaps with both values, and no rule condition matches on it. An account file with no CRM record ID, or an ID that matches no record, adds a gap (needed by: `source-crm-live`). The step is done when you can list the facts, the hypotheses, and every gap, each gap tied to the rule ID, play ID, or source rule ID that needs it.
2. **Decide.** Apply the handoff rules in `brain/stages.md` in order; the first rule that matches decides: `skip`, `route-to-owner`, `act-now`, or `nurture`. Each reason cites evidence. The step is done when every condition of the chosen rule is matched to a quoted line or listed as a gap. When two inputs disagree on a fact, the conflict order in `brain/sources.md` picks the one to use: cite the source rule ID and list the disagreement under Gaps (`source-fix-copy`). A missing read date, map row, or CRM record adds a gap but does not change the decision on its own; the person confirms the value at its source before approving. An unresolved field can change the decision, because no rule condition matches on it.
3. **Pick the play.** For `act-now`, choose the play whose trigger the **current signal** matches. Account activity can shape the angle; it does not pick the play. When the signal matches two plays, the one listed first in `brain/plays.md` wins, and the other goes under Gaps as "person to confirm the play". Write the angle in one sentence. For `nurture` and `skip`, write the next check: what new evidence would change the decision. For `route-to-owner`, write one line for the owner saying what the signal is.
4. **Draft.** For `act-now` only, draft the first touch under the draft rules in `brain/plays.md`. The draft is the message exactly as the recipient would read it: plain sentences, no file paths or citations inside it. Under the draft, list each sentence's evidence. The step is done when every draft sentence is either the ask or restates a **fact** with its meaning intact: the same event, the same people, the same tense (a posted role is still an open role). Cut any sentence that states a hypothesis, a judgment, or anything no brain file holds. A gap that blocks a detail or the send path (for example, no verified email) stays under Gaps.
5. **Log and stop.** Write `brain/decisions/<today's date>-<company>-<signal file name>.md`, using the date the decision is made, in the format below with `status: proposed`. When that file already exists, stop and tell the person; a decision file is never overwritten. Then show the person the decision, the gaps, and the draft. The run is done when the file exists and every claim in it cites evidence or sits under Gaps.

## Write boundary

The skill writes new files in `brain/decisions/`, verdict fields in an existing decision file, and new lines in `brain/corrections.md`. The one exception is Branch B step 3. Sending, CRM writes, and stage changes belong to the person who approves.

## Branch B: record a verdict

When a person approves, edits, or rejects a proposed decision:

1. Set `status` to `approved`, `edited`, or `rejected` in the decision file, and fill `verdict_reason` with their words.
2. For `edited` or `rejected`, append one line to `brain/corrections.md`: date, company, what was wrong, and the one ID it points at (a rule ID from `brain/stages.md`, a play ID or draft rule ID from `brain/plays.md`, or a source rule ID from `brain/sources.md`).
3. Count lines in `brain/corrections.md` by ID. When one ID reaches three lines, show the person the exact edit you propose to that rule, play, or source rule. When they say yes to that exact text, write that one edit to that one file. That is the only write outside `brain/decisions/` and `brain/corrections.md`.

## Decision file format

```markdown
---
account: <company>
signal: brain/signals/<file>
decision: act-now | nurture | skip | route-to-owner
rule: <rule ID from brain/stages.md>
play: <play ID or none>
status: proposed
decided_at: <YYYY-MM-DD>
verdict_reason:
---

## Facts
- <fact> (brain/<file>: "<quoted line>")
- <copy> (brain/<file>: "<quoted line>", read <YYYY-MM-DD>)
- <CRM value> (brain/crm-export/companies.csv <company_id>: <column> = "<value>", read <YYYY-MM-DD>)

## Hypotheses
- <hypothesis> (brain/<file>: "<quoted line>")

## Gaps
- <missing fact> (needed by: <rule ID, play ID, or source rule ID>)

## Decision
<decision>, by <rule ID>, because:
- <reason> (brain/<file>: "<quoted line>")

## Play and angle
<play ID>: <one-sentence angle>. Or the next check (nurture, skip), or the owner note (route-to-owner).

## Draft (DRAFT, not sent)
To: <named contact, or the role when no contact is named>

<the message, or "none">

Draft evidence:
- Sentence 1: brain/<file>: "<quoted fact>"
- Last sentence: the ask (<play ID> offer)
```
