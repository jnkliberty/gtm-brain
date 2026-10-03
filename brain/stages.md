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
   - the current signal matches one play's trigger in `brain/plays.md`.
4. **`rule-nurture`: nurture** in every other case, including a missing or unfamiliar `relevanceVerdict` (list it under Gaps). Name the next check that would move the account to act now.

A missing contact or email does not change the decision. It goes under Gaps and blocks only the send.
