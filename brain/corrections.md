# Corrections

One line per edited or rejected decision. Each line has seven fields, separated by ` | `, so no field contains that separator:

```
- <date> | <company> | decision: <decision file path> | wrong: <what was wrong> | source: <file>: "<quoted text>", or none | applies when: <one short condition> | points at: <ID>
```

- `decision:` is the path of the decision file the verdict is on, for example `brain/decisions/<date>-<company>-<signal>.md`.
- `source:` is the line the person disputes, as a file and the exact quoted text. Write `none` when no source line is disputed.
- `applies when:` is one short condition that says when the lesson holds, for example "the signal is a hiring post with no date". Write "this account only" when the lesson is a one-off.
- `points at:` holds exactly one ID: a rule ID from `brain/stages.md` (for example `rule-act-now`), a play ID or draft rule ID from `brain/plays.md` (for example `first-gtm-hire` or `draft-length`), or a source rule ID from `brain/sources.md` (for example `source-export-copy`).

A rule edit needs three independent matching failures: three lines with the same `points at` ID, the same `applies when` condition, and three different accounts, each with its own decision file. A line whose `applies when` is "this account only" never counts. When three lines qualify, the skill proposes an edit, starting with the line `Proposed rule edit: <ID>`, to that rule, play, or source rule and cites the three lines and their decision files.

## Lines

