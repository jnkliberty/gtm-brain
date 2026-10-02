# CRM export format

The skills read `companies.csv` and `contacts.csv` when no live CRM connection is available. The two `candidates-*.csv` files are invented vendor inputs for build skills. Export from any CRM into these columns. Every company, person, and value in the example files is invented. Sample domains and profile URLs use reserved `.example` hosts.

## companies.csv

| Column | Meaning |
| --- | --- |
| `company_id` | The CRM's record ID |
| `name`, `domain` | Company name and primary web domain |
| `segment` | `B2B` or `B2C` |
| `industry` | Free text |
| `employees` | Headcount |
| `revenue_detected` | Annual revenue in USD from enrichment. Automation may overwrite it. |
| `revenue_confirmed`, `revenue_confirmed_at` | Annual revenue a person confirmed, and the date they confirmed it. Automation never overwrites it. |
| `crm_detected` | The CRM the company uses, from enrichment. |
| `crm_confirmed`, `crm_confirmed_at` | The CRM a person confirmed, and the date. |
| `has_gtm_engineer` | `yes`, `no`, or `unknown` |
| `hq_country` | Two-letter country code |
| `stage` | Target, Engaged, Sales-ready, or Opportunity (see `brain/stages.md`) |
| `owner` | Account owner, empty when unassigned |
| `last_activity_at` | Date of the last recorded activity |
| `source` | Where the record came from: a vendor ID such as `vendor-a` or `vendor-c`, `manual`, or `form` |

## contacts.csv

| Column | Meaning |
| --- | --- |
| `contact_id`, `company_id` | The contact's ID and the company it belongs to |
| `first_name`, `last_name`, `title`, `function` | Who they are |
| `email` | Work email |
| `email_status` | `valid`, `invalid`, `catch-all`, `unknown`, or empty (never checked) |
| `linkedin_url` | Profile URL |
| `linkedin_current_company` | The employer the profile shows today, from enrichment |
| `country`, `owner`, `last_activity_at`, `has_open_deal` | As named |
| `source` | Where the record came from |

## candidates-accounts.csv

`candidate_id` identifies a vendor row, not a CRM record. `name`, `domain`, `segment`, `industry`, `employees`, `has_gtm_engineer`, and `hq_country` have the company meanings above. `revenue` is detected annual USD revenue; `crm` is the detected CRM. `source` names the vendor. Candidates have no confirmed values, stage, or owner.

## candidates-contacts.csv

`candidate_id` identifies a vendor row, not a CRM record. `company_domain` links to a company domain or proposed account domain. Name, title, function, email, email status, LinkedIn URL, country, and source have the contact meanings above. Candidates have no activity, deal, or owner fields.

## ceiling-contacts.csv

Synthetic add-on for testing the contact ceiling. Combine its rows with `contacts.csv` only for that test; normal runs read `contacts.csv` alone.

## move-evidence.csv and move-contacts.csv

Synthetic work-history evidence for `contact-move-routing` and `contact-retention-review`. `case_id` identifies a test observation; `contact_id` links to a current contact. `profile_url` and `person_name` must match that contact before an observation can classify a move. Origin and destination names, domains, titles, role dates, `observed_at`, and `source` preserve the evidence behind the decision. `move-contacts.csv` adds two invented duplicate contact rows for the move test; combine it with `contacts.csv` only for that test. An employer-name mismatch in `contacts.csv` alone is a review flag.
