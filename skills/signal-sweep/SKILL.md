---
name: signal-sweep
description: "Use when the team wants every new signal turned into a decision in one run, for example each weekday morning. Runs account-handoff on each signal in brain/signals/ that has no decision yet, strongest first, and reports only the accounts that need a person. Says one line when nothing does, and warns when the signal feed has gone stale."
license: MIT
---

# Signal sweep

Turns every new signal into a proposed decision, then tells the person only what needs them. The decisions come from the `account-handoff` skill. The sweep owns which signals run, in what order, and what the person hears.

## Quiet by default

**Quiet** is the leading word. The person hears about an account only when someone has to act on it.

- A **new signal** is a file in `brain/signals/` with no decision yet: no file in `brain/decisions/` whose name ends with `-<signal file name>`. A signal whose latest decision (the one no other decision names in `supersedes`) has the gap "handoff budget full" (needed by: `rule-handoff-budget`) and any status except `rejected` counts as new again on a later day; on the day it was held, it waits for the next sweep.
- A **handoff** is a decision of `act-now` or `route-to-owner`. Each one is reported in full.
- `nurture` and `skip` decisions are logged as usual and reported only as a count.
- A **stale feed** is one whose newest signal file is dated more than 7 days before today, by the date in its file name. A stale feed is reported first, even when there are no new signals: a quiet sweep over a dead feed looks the same as a quiet week. An empty `brain/signals/` is reported the same way: "No signals in `brain/signals/`. Check the signal feed."

## Steps

1. **Find new signals.** List the files in `brain/signals/`, read the date in each file name, and keep the new signals. Match each one to the account file in `brain/accounts/` for the company it names. A signal that names no account with a file there is not decided; it goes in the report as "no account file". The step is done when every signal file is marked new or decided, every new signal has an account file or is marked "no account file", and the newest signal date is known.
2. **Order them.** Put signals held back by the budget on an earlier sweep first, then the rest. Sort each group by `signalStrength` (High, then Medium, then Low or missing), then by the date in the file name, oldest first. The handoff budget goes to the strongest signals first and, among equals, to the one closest to going stale. The step is done when the list has a single order.
3. **Decide each, in order.** For each new signal, run `account-handoff` Branch A for its account, one at a time, so each decision counts the ones before it against `rule-handoff-budget`. Its step 5 report goes into the sweep report below instead of being shown alone. The step is done when every new signal with an account file has a decision file.
4. **Report.** Show the person, in this order, and leave out any part that is empty:
   - The stale feed: "The newest signal is from <date>, <n> days ago. Check the signal feed." Or the empty-feed line.
   - Each handoff, `act-now` first in the order decided, then `route-to-owner`: the account, the decision, the rule, the play, the draft or owner note, the gaps, and the decision file path.
   - Handoffs still `proposed` from earlier runs, today's included (skip any a later decision names in `supersedes`), one line each: the account, the decision, and the decision file path. This catches a handoff an interrupted sweep never reported.
   - Accounts held back by `rule-handoff-budget`: they are first in line on the next sweep.
   - `nurture` decisions where a missing or unresolved input kept a `rule-act-now` condition from matching, such as no `relevanceVerdict` or two stages that disagree, whatever rule ID the gap names. Show the account, the gap, and the decision file path. A person fixes the input, then runs `account-handoff` for that signal on a later day, since today's decision file already exists.
   - Signals with no account file, by file name.
   - One line: "<n> nurture and <n> skip, logged in `brain/decisions/`." Accounts held back by the budget or listed for a missing or unresolved input are not counted here.

   When the first six parts are empty, the whole report is one line: "No handoffs today." followed by the count. The step is done when every new signal appears in exactly one part of the report, and every handoff still `proposed` from an earlier run is listed.

## Write boundary

The sweep writes only what `account-handoff` writes: new decision files. It starts no schedule. A team that wants it every morning runs `Run signal-sweep.` from its own scheduler.
