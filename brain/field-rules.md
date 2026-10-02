# Field rules

Some values come from enrichment and some from a person. They live in separate fields so automation never overwrites what a person confirmed. Corrections point at these IDs.

## Field pairs

| Rule ID | Detected field (automation may write) | Confirmed field (person only) | Confirmation date |
| --- | --- | --- | --- |
| `field-revenue` | `revenue_detected` | `revenue_confirmed` | `revenue_confirmed_at` |
| `field-crm` | `crm_detected` | `crm_confirmed` | `crm_confirmed_at` |

## Rules

- `rule-confirmed-wins`: anything that reads the value (tiering, filters, reports) uses the confirmed field when it has a value, and the detected field only when the confirmed field is empty.
- `rule-no-overwrite`: automation and skills never change a confirmed field. A change to a confirmed field is proposed to a person, who makes it.
- `rule-dated`: a confirmed value carries its confirmation date. A confirmed value with no date is flagged for the owner to date or re-confirm.
- `rule-dated-protected`: a confirmation date is part of the confirmed value. It gets the same protection as `rule-no-overwrite`.
- `rule-disagree`: numbers disagree when they differ by more than 10% of the confirmed value; text disagrees on any difference. When the detected and confirmed values disagree, the confirmed value stands and the disagreement is reported, because it can mean the confirmed value went stale or the enrichment source is wrong.
