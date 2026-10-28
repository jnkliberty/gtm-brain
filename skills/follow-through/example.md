# Fictional call and paste use

This example is invented. It contains no customer information.

## Try the call

Read `SKILL.md`, then paste this request:

```text
Run follow-through in chat only. Do not write files. I permit use of these fictional notes.
Company: Cedar Labs. Seller: Mira. Customer: Theo. Call date: 2026-10-20.
[00:10] Theo: We agreed to test the contact export with ten rows.
[00:20] Mira: I will send the ten-row export on 2026-10-22.
[00:30] Theo: I will review the export on 2026-10-23 and reply with any missing fields.
No actions are reported complete. Draft a message to Theo. I will review it myself.
```

The result can be Ready without a call ID or send permission. A generated local record ID does not change the call facts.

## Use without the repository

1. Paste the full `SKILL.md` into the assistant chat.
2. Supply the call, permission to use it, and the company label.
3. State `Use supplied context only. Do not write files.`
4. Answer up to five company-fact questions if needed.
5. Retain the full reusable record, including source excerpts and the final `outcome_log`.

For the next run, paste the skill and that record again. Add your name, verdict, correction, or reported outcome.
For example: `Mira rejects this draft: the export date should remain unknown. Apply only to this account.`
That example is feedback, not evidence that any export was sent. A new draft needs a new proposal record.

Codex CLI cases pass the final checks. Grok review is complete; its final finding was rejected after replay of the saved traces. Claude checks are deferred. Claude and browser-chat behavior remain unverified.
