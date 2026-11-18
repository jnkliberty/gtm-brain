---
description: "How an outcome readback compares a baseline window with a candidate window: the declared metric, people-based rates, minimum volume, the opt-out guard, confounders, and the order that picks promote, keep-testing, roll-back, or unproven. Read it before you run or review a readback."
---

# Readback rules

A readback answers "did the change work?" for one change record in `brain/changes/`. `scripts/readback_count.py` does every count. These rules turn the counts into one proposed decision. A person approves the decision and makes any edit it proposes. The numbers below are starting values; edit them here, never inside a skill.

## Metric

- **`readback-declared`:** the change record names one `primary_metric` and a `declared_at` date on or before the first touch in the candidate window. A missing metric, a missing `declared_at`, or a date after that first touch gives `unproven`. A metric chosen after results came in cannot prove a change.
- **`readback-metrics`:** the primary metric is one of these. Each rate is a count of distinct people over the delivered people in the window.
  - `reply-rate`: people with any reply except `auto-reply`. A reply with a `replied_at` date and a blank `reply_class` counts here and is listed as unclassified.
  - `positive-reply-rate`: people with an `interest`, `question`, or `referral` reply.
  - `meeting-rate`: people with a `meeting_booked_at` date.

  Any other metric name gives `unproven`, with the name quoted.
- **`readback-guard`:** the guard metric is always `opt-out-rate`: people with an `opt-out` reply over delivered people. The candidate's guard is worse when its opt-out rate is 2 or more percentage points above the baseline's.

## Counting

- **`readback-people`:** rates count people, not touches. A person is the `contact_id`; when it is blank, the email; when that is blank, the LinkedIn URL. A person who replied on two touches counts once. A person whose every touch in the window bounced leaves the denominator; a person with one bounced and one delivered touch stays in it. Only `outbound` rows count. Inbound rows are listed by `touch_id` and left out.
- **`readback-windows`:** the candidate window holds the outbound touches whose `change_id` is the change's ID, from the first to the last `sent_at`. The baseline window holds the untagged outbound touches on the same channels in the 28 days before `changed_at`. When the person names both windows as dates, those dates win and every outbound touch sent inside each window counts.
- **`readback-min-volume`:** each window needs at least 20 delivered people. Below that, the decision is `unproven`, and the readback shows the people sent, the people who bounced only, and the delivered people for both windows.
- **`readback-fresh`:** the touches export is dated by the read date the person gives. With none given, use the export date named in the "Outreach touches and replies" row of `brain/sources.md`, and say that is the date used. Its freshness limit is that row's "Fresh for" days, counted to the date of the run. A stale export, a missing export, no read date from either place, or no row in `brain/sources.md` (`source-unmapped`) gives `unproven`, with the age in days, or the missing item, stated.

## Confounders

- **`readback-confounders`:** list every one of these that holds, with the values from both windows. A confounder is never hidden and never explained away.
  - Different sender: the two windows' `sender` sets differ.
  - Different list source: the two windows' `source` sets differ.
  - Overlapping change: another change ID appears on a touch inside the candidate window, or another change record has a `changed_at` inside it.
  - Open window: fewer than 14 days have passed since the last candidate touch. Replies may still arrive.

## Decision

- **`readback-lift`:** the candidate wins the primary metric when its rate is 5 or more percentage points above the baseline's, and loses it when its rate is 5 or more points below.
- **`readback-decide`:** the first matching line decides. Name its rule ID in the readback.
  1. `unproven`: `readback-declared`, `readback-metrics`, `readback-fresh`, or `readback-min-volume` fails, or the change record is missing.
  2. `roll-back`: the guard is worse (`readback-guard`), whatever the primary metric shows.
  3. `keep-testing`: the candidate window is still open.
  4. `keep-testing`: a different sender, a different list source, or an overlapping change holds.
  5. `promote`: the candidate wins the primary metric (`readback-lift`).
  6. `roll-back`: the candidate loses the primary metric (`readback-lift`).
  7. `keep-testing`: the difference is under 5 points either way.
- **`readback-promote-edit`:** a `promote` decision proposes the edit as text for a person: which file, which line, and the new wording. The readback never makes the edit. A play, rule, or brain file changes only when a person edits it.
