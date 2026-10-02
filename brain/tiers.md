# Tiers (example)

Tiers decide how much effort an account gets. Replace the thresholds with your own. Corrections point at these IDs.

## Rules

- `tier-check-revenue-first`: before setting a tier, check the revenue value. Revenue per employee must fall between $20,000 and $2,000,000. A value outside that range is not used for tiering; the account is escalated with the value and the reason.
- `tier-confirmed-wins`: tiering reads `revenue_confirmed` when it has a value, and `revenue_detected` only when it is empty (`rule-confirmed-wins` in `brain/field-rules.md`).
- `tier-1`: ICP fit and revenue of $40 million or more.
- `tier-2`: ICP fit and revenue from $20 million up to $40 million.
- `tier-3`: ICP fit and revenue under $20 million.
- `tier-none`: fails the ICP. No tier; not built.
