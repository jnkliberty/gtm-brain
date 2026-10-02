# Call rules (example)

The notes in this starter brain are invented and private. Replace the rules with your team's approved call process.

- `call-confirmed`: treat one exact excerpt as a fact only when its own `rep_confirmed` is `yes`, its confirmation date is valid and no later than the review date, and the quote supports its `claim_value`. Another excerpt on the same call cannot confirm it.
- `call-claim`: `present` means the excerpt says the pain occurs; `absent` means it says the pain does not occur. Keep the exact quote, call ID, quote ID, and source beside either claim.
- `theme-two-domains`: propose a recurring pain only when confirmed `present` excerpts with the same `pain_key` come from at least two unique domains in `brain/crm-export/companies.csv`. Resolve `company_id` to that domain before counting; duplicate company records at one domain count once.
- `call-conflict`: confirmed `present` and `absent` excerpts for one pain at one resolved company domain are unresolved, including when duplicate company IDs share that domain. Exclude that domain's evidence for the pain until a person resolves the conflict.
- `call-private`: call excerpts remain in the internal theme file. Label inferences as hypotheses and missing facts as gaps. Keep any repo with real call notes or theme files private; this public starter contains invented excerpts only.
- `draft-public-only`: this call review creates no outreach draft or published claim. A person must separately clear any claim for external use.
