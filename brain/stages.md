# Stages and handoff rules

Who owns an account at each stage, and what moves it. Marketing and sales both read and write these records. Edit this file to change the team's policy.

## Stages

| Stage | Owner | Entry rule |
| --- | --- | --- |
| Target | Marketing | The account matches `brain/icp.md` or the ICP line in its account file. |
| Engaged | Marketing | Someone at the account engaged with our content, events, or site in the last 60 days. |
| Sales-ready | Sales | A handoff rule below says `act-now` and a person approved the decision. |
| Opportunity | Sales | A meeting is booked and the account agreed to a next step. |

## Handoff rules

Apply them in order. The first rule that matches decides. Corrections point at these IDs.

1. **`rule-skip`: skip** when the signal's `relevanceVerdict` is `not_relevant`, or the account file says the account fails the ICP.
2. **`rule-route-to-owner`: route to owner** when the account is at stage Sales-ready or Opportunity. Sales already owns it: log the signal for the owner and write no draft.
3. **`rule-act-now`: act now** when all of these hold:
   - the signal's `relevanceVerdict` is `relevant`,
   - the account is at stage Target or Engaged and fits the ICP,
   - the signal's `signalStrength` is High or Medium,
   - the signal has a concrete `whyNow`: it names the event and the event's calendar date (a relative date such as "two days ago" is not concrete),
   - the current signal matches one play's trigger in `brain/plays.md`,
   - the handoff budget has room (`rule-handoff-budget` below).
4. **`rule-nurture`: nurture** in every other case, including a missing or unfamiliar `relevanceVerdict` (list it under Gaps). Name the next check that would move the account to act now.

A missing contact or email does not change the decision. It goes under Gaps and blocks only the send. `rule-handoff-contract` below says what each handoff must name and how a missing part is reported.

## Handoff contract

**`rule-handoff-contract`:** an `act-now` or `route-to-owner` decision is a message to a named person with a reason. The contract does not pick the decision; it makes a missing part visible. Check three parts and list each unmet part under Gaps with the wording below (needed by: `rule-handoff-contract`). The decision, rule, and play stay as the rules above set them, and the draft rules in `brain/plays.md` still apply.

| Part | `act-now` | `route-to-owner` | Comes from (`brain/sources.md`) | Gap when unmet |
| --- | --- | --- | --- | --- |
| Recipient | The contact the account file names, with a row in `brain/crm-export/contacts.csv` for the account's `company_id` whose `email_status` is `valid` | The company's `owner` | Contact: "Account history and marketing activity" and "Company and contact records". Owner: "Deal stage, amount, and owner" | `no recipient: <why>` (no contact named, or no valid email) |
| Follow-up owner | The company's `owner`, who works a reply | The same person as the recipient | "Deal stage, amount, and owner" | `no owner` |
| Reason | The event and its calendar date, quoted from the signal's `whyNow` | The same, in the owner note | "Signals on accounts" | `no dated reason` |

- Owner and email come from the export, a copy: cite the read date and let `source-export-copy` settle a disagreement. A blank `owner`, or "none assigned" in the account file, means no owner. Never take the owner from a contact row or guess one.
- A missing part never ships silently. The decision stays as decided, the gap is written down, and `signal-sweep` reports it with the handoff. For `act-now`, the draft's `To:` line follows `draft-recipient` (the named contact, the role, or `none`). For `route-to-owner` with no owner there is nobody to route to: write no draft, and the person who approves names an owner.
- A skill never fills a part in. The person who approves names the recipient or owner at its source, then runs the handoff again on a later day, since today's decision file already exists. The new decision names the earlier one in `supersedes`.

## Handoff budget

**`rule-handoff-budget`:** at most 5 `act-now` decisions in any 7 days. Count the files in `brain/decisions/` with `decision: act-now`, a `decided_at` date in the 7 days ending today, any status except `rejected`, and no later decision naming them in its `supersedes` field. When the count is 5 or more, `rule-act-now` does not match: decide `nurture`, add the gap "handoff budget full" (needed by: `rule-handoff-budget`), and the account is first in line on the next sweep. Set the number to how many new accounts your sales team can work in a week. A handoff sales cannot get to is worse than none.
