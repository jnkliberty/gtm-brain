---
description: "How an outcome readback compares a baseline window with a candidate window: the declared metric, people-based rates, minimum volume, the opt-out guard, confounders, and the order that picks promote, keep-testing, roll-back, or unproven. Read it before you run or review a readback."
---

# Readback rules

A readback answers "did the change work?" for one change record in `brain/changes/`. `scripts/readback_count.py` does every count. These rules turn the counts into one proposed decision. A person approves the decision and makes any edit it proposes. The numbers below are starting values; edit them here, never inside a skill.

## Thresholds

`scripts/readback_count.py` reads these six lines and nothing else in this file for its numbers. Change a number only on its line. Keep the format `- threshold <name>: <whole number>`. A `-points` number runs from 1 to 100, every other number from 1 to 3650. If a line is missing, appears twice, or is out of range, the script stops and names it. Threshold lines outside this section are ignored.

- threshold lift-points: 5
- threshold guard-points: 2
- threshold min-people-difference: 3
- threshold baseline-days: 28
- threshold min-delivered-people: 20
- threshold open-window-days: 14

The rules below name each threshold in backticks.

## Metric

- **`readback-declared`:** the change record names one `primary_metric` and a `declared_at` date on or before the first touch in the candidate window. A missing metric, a missing `declared_at`, or a date after that first touch gives `unproven`. A metric chosen after results came in cannot prove a change.
- **`readback-metrics`:** the primary metric is one of these. Each rate is a count of distinct people over the delivered people in the window.
  - `reply-rate`: people with any reply except `auto-reply`. A reply with a `replied_at` date and a blank `reply_class` counts here and is listed as unclassified.
  - `positive-reply-rate`: people with an `interest`, `question`, or `referral` reply.
  - `meeting-rate`: people with a `meeting_booked_at` date.

  Any other metric name gives `unproven`, with the name quoted.
- **`readback-guard`:** the guard metric is always `opt-out-rate`: people with an `opt-out` reply over delivered people. The candidate's guard is worse when its opt-out rate is `guard-points` or more percentage points above the baseline's and `readback-min-difference` holds.

## Counting

- **`readback-people`:** rates count people, not touches. A person is the `contact_id`; when it is blank, the email; when that is blank, the LinkedIn URL. A person who replied on two touches counts once. A person whose every touch in the window bounced leaves the denominator; a person with one bounced and one delivered touch stays in it. Only `outbound` rows count. Inbound rows are listed by `touch_id` and left out.
- **`readback-windows`:** the candidate window holds the outbound touches whose `change_id` is the change's ID, from the first to the last `sent_at`. The baseline window holds the untagged outbound touches on the same channels in the `baseline-days` days before `changed_at`. When the person names both windows as dates, those dates win and every outbound touch sent inside each window counts.
- **`readback-min-volume`:** each window needs at least `min-delivered-people` delivered people; the script reports this as `min_volume_met`. Below that, the decision is `unproven`, and the readback shows the people sent, the people who bounced only, and the delivered people for both windows.
- **`readback-fresh`:** the touches export is dated by the read date the person gives. With none given, use the export date named in the "Outreach touches and replies" row of `brain/sources.md`, and say that is the date used. Its freshness limit is that row's "Fresh for" days, counted to the date of the run. A stale export, a missing export, no read date from either place, or no row in `brain/sources.md` (`source-unmapped`) gives `unproven`, with the age in days, or the missing item, stated.

## Confounders

- **`readback-confounders`:** list every one of these that holds, with the values from both windows. A confounder is never hidden and never explained away.
  - Different sender: the two windows' `sender` sets differ.
  - Different list source: the two windows' `source` sets differ.
  - Overlapping change: another change ID appears on a touch inside the candidate window, or another change record has a `changed_at` inside it.
  - Open window: fewer than `open-window-days` days have passed since the last candidate touch; the script reports this as `window_open`. Replies may still arrive.

## Decision

- **`readback-lift`:** the candidate wins the primary metric when its rate is `lift-points` or more percentage points above the baseline's, and loses it when its rate is `lift-points` or more points below. A win or a loss also needs `readback-min-difference`.
- **`readback-min-difference`:** a win, a loss, or a worse guard also needs the candidate count to differ from the count the baseline rate would predict for the candidate's delivered people by at least `min-people-difference` people. Example: 2 of 20 against 3 of 20 is 5 points, but the baseline rate predicts 2 people and the candidate has 3, a difference of 1 person. The script lists each metric that meets its points threshold with too few people in `too_few_people`.
- **`readback-decide`:** the first matching line decides. Name its rule ID in the readback.
  1. `unproven`: `readback-declared`, `readback-metrics`, `readback-fresh`, or `readback-min-volume` fails, or the change record is missing.
  2. `roll-back`: the guard is worse (`readback-guard`), whatever the primary metric shows.
  3. `keep-testing`: the candidate window is still open.
  4. `keep-testing`: a different sender, a different list source, or an overlapping change holds.
  5. `unproven`: the primary metric or the guard meets its points threshold with fewer than `min-people-difference` people (`readback-min-difference`). State each metric, its points, and its people difference.
  6. `promote`: the candidate wins the primary metric (`readback-lift`).
  7. `roll-back`: the candidate loses the primary metric (`readback-lift`).
  8. `keep-testing`: the difference is under `lift-points` points either way.
- **`readback-promote-edit`:** a `promote` decision proposes the edit as text for a person: which file, which line, and the new wording. The readback never makes the edit. A play, rule, or brain file changes only when a person edits it.
