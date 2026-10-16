---
description: "The three writing checks that code counts exactly: repeated phrase, long sentence, and banned phrase. Read it before you check a draft."
---

# Writing rules (example)

Three checks that code can count exactly. `scripts/content_checks.py check` runs all three on every draft. There is no keyword density target.

- `rule-repeat-phrase`: a phrase of 2 to 4 words used more than 3 times in one draft is flagged. Count case-insensitively, after removing punctuation and Markdown marks. A phrase made only of function words (such as "of the" or "in a") is skipped. When a long phrase and a shorter piece of it have the same count, report the long phrase once. The report names the phrase, its count, and this rule ID.
- `rule-long-sentence`: a sentence of more than 25 words is flagged. A sentence ends at a period, exclamation mark, question mark, semicolon, colon, vertical bar, or line break, the same way `rule-repeat-phrase` splits a draft. A word is a run of letters, digits, or apostrophes, so a hyphen or a comma inside a number splits it in two. Markdown marks are not words. The report names the line, the word count, and this rule ID.
- `rule-banned-phrase`: a phrase listed in [`brain/search/banned-phrases.txt`](banned-phrases.txt) is flagged on every line where it appears. The report names the phrase, the line number, and this rule ID.

A flag asks for a rewrite. A person decides whether a flagged phrase or sentence stays.
