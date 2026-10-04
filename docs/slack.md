# Use the GTM brain from Slack

Run the brain's skills from a Slack channel with Claude Tag, Anthropic's Slack product. Claude Tag is in public beta, so details can change. Facts below were checked against the Claude Tag docs on 2026-10-04.

## What you get

- You ask for a skill in a channel: `@Claude Run signal-sweep.`
- The sweep report lands in that channel, one thread per run.
- You review a handoff and record a verdict (approve, edit, reject) in the same thread.

## Rules for this guide

- **Use a private copy.** Your accounts, signals, and verdicts are your company's data.
- **Test in a sandbox Slack workspace you own.** Never test in a client's workspace.
- **Slack never sends and never writes to a CRM.** The skills only propose. Do not give Claude CRM or email credentials.
- **Approvals land in GitHub.** Claude pushes a verdict as a branch or pull request, and a person reviews it there.

## Requirements

| Need | Detail | Source |
| --- | --- | --- |
| Plan | Claude Team or Enterprise. Free, Pro, and Max do not work. | [Set up Claude Tag](https://claude.com/docs/claude-tag/admins/setup-overview) |
| Claude role | An Owner of the Claude organization runs setup. | Same page |
| Slack role | A Slack workspace admin runs `@Claude connect` and usually installs the app. | Same page |
| Org settings | Routines turned on. No Zero Data Retention (ZDR) or customer-managed encryption (CMEK) policy. | Same page |
| Credits | On a Team plan, usage credits loaded, and a monthly spend limit. | Same page |
| GitHub | A GitHub organization owner installs the Claude GitHub App. | [Configure GitHub](https://claude.com/docs/claude-tag/admins/configure-github) |
| Repo | A private or internal repo laid out as a plugin marketplace. A public repo cannot be selected. | [Skills repository](https://claude.com/docs/claude-tag/admins/skills-repo) |

This repo already has the layout: `.claude-plugin/marketplace.json` at the root and the `gtm-brain` plugin.

## Set up

Do every step in the sandbox workspace first.

1. **Make a private copy.** GitHub keeps forks of a public repo public, so copy it instead. Create an empty private repo in your GitHub organization, then run `git clone --bare https://github.com/jnkliberty/gtm-brain.git` and, inside the new `gtm-brain.git` folder, `git push --mirror https://github.com/<your-org>/<your-repo>.git`. Check: the new repo shows "Private" and lists `.claude-plugin/marketplace.json`.
2. **Install the Claude app.** Open [claude.com/claude-for-slack](https://claude.com/claude-for-slack) and choose Add to Slack. Check: Claude appears in the workspace's app list.
3. **Get a pairing code.** A Slack workspace admin posts `/invite @Claude` in a test channel, then `@Claude connect` as a message with no other text. Check: Claude replies with a code only that admin sees. It works once and expires in 15 minutes.
4. **Pair the workspace.** As the Claude Owner, open [claude.ai/admin-settings/claude-tag](https://claude.ai/admin-settings/claude-tag) and paste the code. Choose Specific channel, enter the test channel's ID, and select Pair workspace. For a private channel, invite Claude to it first. Check: "Connected to" and your workspace name appear.
5. **Connect GitHub.** A GitHub organization owner installs the Claude GitHub App (setup has a GitHub step). Then grant the private brain repo in an Access bundle, on its Repositories tab. Claude gets write access to that repo, so protect `main` (see Guardrails).
6. **Launch.** Add credits if asked, set a low monthly spend limit, and choose Launch Claude Tag. Until then, every mention gets "Claude is disabled in this channel." Check: in the test channel, `@Claude summarize what this channel decided this week` gets a threaded reply that ends with a Configure link.
7. **Register the skills.** Open Organization settings > Plugins & skills, choose Add, then Sync from GitHub. Pick the private repo and leave Sync automatically on. Check: the `gtm-brain` plugin appears. Alternative: upload the plugin as a zip.
8. **Attach the plugin.** In the same Access bundle, switch on `gtm-brain` on the Plugins tab, and attach the bundle to the test channel. Check: in a new thread, `@Claude what can you access from this channel?` lists the brain repo.

Sources for steps 2 to 8: the Set up Claude Tag and Skills repository pages above, and [Customize](https://claude.com/docs/claude-tag/admins/customize).

## Daily use

Run a skill by hand:

```text
@Claude Run signal-sweep.
```

Schedule the sweep. Schedules run in UTC, so name your timezone. Anyone in the channel can pause or stop a routine, and `@Claude !routines` lists them ([Set up routines](https://claude.com/docs/claude-tag/users/proactivity)).

```text
@Claude every weekday at 8am Central, run signal-sweep and post the report here.
```

A quiet sweep replies "No handoffs today." and a count, after any stale-feed warning.

Review one handoff:

```text
@Claude Run account-handoff for Northwind Robotics on the 2026-09-24 signal.
```

Record a verdict in the same thread. `account-handoff` Branch B sets `status` to `approved`, `edited`, or `rejected`:

```text
@Claude Approve the Northwind decision.
@Claude Edit the Northwind decision: cut the second sentence. Reason: we have not verified that role.
@Claude Reject the Northwind decision. Reason: wrong play.
```

An edit or a rejection also adds a line to `brain/corrections.md`. Three lines on one rule propose a change to it, and you approve the exact text.

To set up your own brain, one file at a time:

```text
@Claude Run brain-setup.
```

## Guardrails

- **No sends, no CRM writes.** The rule comes from `AGENTS.md`, not Slack.
- **Approvals land in GitHub.** Claude Tag pushes file changes back as a branch or pull request ([How it works](https://claude.com/docs/claude-tag/concepts/how-it-works)). On a branch that needs one approving review, the person who asked for the change can approve and merge it alone. Require two approving reviews, or a status check, on the branch Claude opens pull requests against ([Configure GitHub](https://claude.com/docs/claude-tag/admins/configure-github)).
- **Channel work runs under service accounts** that an Owner sets up ([Security and data](https://claude.com/docs/claude-tag/concepts/security-and-data)). The docs name no per-message approval step for channel work, so your gate is the pull request review.
- **Who can call Claude.** By default, anyone in the connected Slack workspace, even without a Claude account. An Owner can limit that to your Claude organization (Team: "Restrict to your organization") ([Restrict access](https://claude.com/docs/claude-tag/admins/restrict-access)).
- **Privacy.** Anthropic keeps session transcripts and memory until you delete them, with no automatic retention period in the beta. No Slack control deletes one thread's transcript, and the Compliance API does not list or delete them. Slack messages stay under your Slack retention settings, a separate copy ([Data lifecycle](https://claude.com/docs/claude-tag/concepts/data-lifecycle)). Keep real accounts, calls, and CRM exports in the private repo only, never in a public repo or a workspace you do not own.

## Test checklist

Sandbox only. Mark each PASS or FAIL.

- [ ] `@Claude summarize...` gets a threaded reply.
- [ ] `what can you access` lists the brain repo and the `gtm-brain` plugin.
- [ ] `Run account-handoff for Northwind Robotics on the 2026-09-24 signal.` returns `act-now`, keeps the "no verified email" gap open, and sends nothing.
- [ ] An Approve reply sets `status: approved` on a branch or pull request, not on `main`.
- [ ] `Run signal-sweep.` on the sample data returns the handoffs, then the nurture and skip count.
- [ ] A scheduled sweep posts at the set time.
- [ ] Nothing was sent and no CRM changed. Check the pull request diff.
- [ ] After you turn on the member restriction, someone without a Claude account cannot invoke Claude.
- [ ] After you change a brain file or skill through a pull request, `python3 evals/run.py` still passes locally.

## Open questions

1. **Which plan, Team or Enterprise?** Julian decides.
2. **Which sandbox Slack workspace?** Julian decides.
3. **Do skills see the repo's `brain/` files?** The docs say Claude clones granted repos and loads their `CLAUDE.md`. They do not say the skill's working folder is that clone. Checklist item 3 answers it.
4. **Does a verdict arrive as a branch, a pull request, or a direct push?** The docs say "a branch or pull request" for edits in general. Checklist item 4 answers it.
5. **Cost.** Usage draws from an organization balance. The docs give no per-sweep price. Check after a week.
6. **Not checked:** Enterprise Grid setup, `/install-slack-app`, and DM behavior.
