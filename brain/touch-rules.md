---
description: "Example rules for checking a person against the suppression list and past outreach before a new contact or first touch: how a person matches, what an opt-out blocks, how long a touch holds, and when coverage is too thin to say clear. Read it before you run or review a prior-touch check."
---

# Touch rules (example)

When a person may get a new contact record or a first touch. The data lives in `brain/crm-export/touches.csv` and `brain/crm-export/suppression.csv`; [crm-export/README.md](crm-export/README.md) defines their columns. Replace the numbers with your own. Corrections point at these IDs.

## Matching a person

Every rule below matches a person the same way.

- An email matches when the two addresses are equal after trimming spaces and ignoring case.
- A LinkedIn URL matches when the two are equal after ignoring case and removing `https://`, `http://`, `www.`, and a trailing `/`.
- A `contact_id` matches when both rows carry the same CRM contact ID.
- A name never matches, alone or with a title. Two people with one name and different emails are two people.
- A shared company domain never matches a person. Only `touch-suppress-company` uses a domain.
- A person's domain is the part of their email after `@`, or the company domain supplied with them.

## Rules

- `touch-suppress-person`: a `person`-scope row in `suppression.csv` that matches the person by email or LinkedIn URL blocks that person. Its `company_domain` describes the person only; it never covers a colleague.
- `touch-suppress-company`: a `company`-scope row blocks every person whose domain equals its `company_domain`, ignoring case and a leading `www.`.
- `touch-optout-all-channels`: an opt-out blocks every channel (email, LinkedIn, phone, event, other), not only the channel it arrived on. It never expires: an `expires_at` on an opt-out row is reported and ignored. A `touches.csv` row that matches the person and has `reply_class` `opt-out` blocks them the same way, even with no suppression row. That case also proposes a suppression row for a person to add.
- `touch-expiry`: a suppression row with any reason other than `opt-out` blocks until its `expires_at`. On the run date or later the row is expired: report it, and it does not block. An empty `expires_at` never expires.
- `touch-recent`: a touch to the person, outbound or inbound, with `sent_at` within the last 30 days before the run date (the run date counts as day 0) gives `hold`. Show the last touch date, channel, direction, sender, delivery status, and any reply. A touch older than 30 days is reported and does not hold. A touch to a colleague at the same domain is context, never a hold.
- `touch-coverage`: before any person can be `clear`, both `touches.csv` and `suppression.csv` must exist and be fresh. Each file's date and "Fresh for" days come from its row in [sources.md](sources.md). A missing, unreadable, or stale file gives `unknown`, never `clear`. Every result states which files were read and their dates. No match in the files is not proof of no contact.

## Status order

Each person gets one status. The first that applies wins.

1. `blocked`: an active suppression row or an opt-out reply matches (`touch-suppress-person`, `touch-suppress-company`, `touch-optout-all-channels`). A block found in one file stands even when the other file is missing.
2. `unknown`: a file is missing or stale (`touch-coverage`), or the person has no email, no LinkedIn URL, and no contact ID to match on.
3. `hold`: a recent touch matches (`touch-recent`).
4. `clear`: both files are fresh, and neither holds a matching active row or recent touch.
