# Contact rules (example)

Which people to hold at each account, how many, and when to let a record go. Replace the numbers with your own. Corrections point at these IDs.

## Building contacts

- `contacts-functions`: target functions are Executive, Sales, RevOps, and Marketing at every tier.
- `contacts-opening-pull`: a new build fills each account to its opening pull: Tier 1: 5, Tier 2: 4, Tier 3: 3 contacts in target functions.
- `contacts-ceiling`: ceilings are Tier 1: 15, Tier 2: 8, Tier 3: 5. Count every current contact record at the account, across all functions and email statuses. An account above its ceiling is escalated to its owner, never trimmed.
- `contacts-order`: when adding contacts, add in this order: RevOps, Sales, Marketing, Executive. Within a function, the more senior title first.
- `contacts-audit-first`: count and check the contacts an account already has before adding new ones.
- `contacts-valid-email`: a contact counts toward the opening pull only with an email whose status is `valid`. No contact is proposed with an email that is not `valid`.

## Keeping contacts

- `keep-protected`: keep a contact who has an open deal, has activity in the last 12 months, or belongs to an account at stage Opportunity. A protected contact is kept even when another rule would archive it.
- `archive-wrong-function`: propose archiving a contact outside the target functions at an ICP account, unless `keep-protected` applies.
- `departed`: a different `linkedin_current_company` name is a review flag, not proof of departure. Apply `move-verified` before proposing a restorable departure archive for an unprotected contact. A name mismatch alone never changes `company_id` or creates an owner task. Contact move routing owns owner tasks.
- `move-verified`: match the evidence profile URL and person name to the contact. A contact with no evidence row gets `no move evidence` and no move label. An evidence row linked by contact ID or profile URL but with a conflicting identity is `uncertain`. Compare normalized company domains, not employer names or legal suffixes. Use the CRM company domain as the origin anchor. A same-domain, same-title current role is `same role`; a same-domain new title with a dated start is `changed role`; a different-domain active destination with a dated start and a valid end date for the origin role is a `confirmed move`. Keep the origin role in the record of the decision. Unmatched identity, name-only origin, missing or invalid required date, future role date, observation after review date or over 90 days old, origin-domain mismatch, simultaneous active roles at different domains, conflicting recent current employers, or destination title containing `advisor`, `fractional`, or `consultant` is `uncertain`. Apply these uncertainty checks before assigning another label. An uncertain result creates no move action.
- `hold-unverified`: a contact whose email status is `catch-all`, `unknown`, `invalid`, or empty is held and labeled unverified. Hold is not archive.
- `keep-scope`: this review covers contacts at ICP accounts only. Contacts at accounts outside the ICP are left as they are.
- `archive-restorable`: an archive is proposed as restorable. Nothing is deleted.
