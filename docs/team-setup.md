# Set up shared GTM context for your team

Use this guide to prepare shared company context for sales and marketing. Start with approved business definitions, then plan how people and tools use them.

The starter supports account readiness and marketing-to-sales handoff. It does not provide a complete deal qualification process.

## Before you start

Use a private repository or a private local copy before you add real company data. A public fork remains public. Do not put credentials in the brain or the worksheet.

The [deployment worksheet](./deployment-plan-template.md) records proposals. It grants no permission to change access, connect tools, sync records, send messages, or write to a CRM.

All prompts below draft in chat. On your explicit request, the agent may save a new dated worksheet under `brain/setup/`. Use a unique filename such as `YYYY-MM-DD-team-deployment.md`. If it exists, stop and choose another name; never overwrite a worksheet. Save instruction drafts inside that worksheet, not in active instruction files. Leave unanswered items as `GAP: <question or missing source>`.

The existing [brain-setup skill](../skills/brain-setup/SKILL.md) keeps its interview, fixed rule IDs, record handling, and exact-text approval boundary. This guide adds no skill mode. Approval of a worksheet does not approve changes to policy files or live systems.

## 1. Gather approved business definitions

Identify who owns customer criteria, stages, plays, and source authority. Gather links to reviewed definitions and record their approver and review date. Separate approved definitions from examples and unresolved answers.

Use the existing brain-setup interview when those four policy files need your team's answers. It writes each policy file only after approval of its exact text. Do not use a worksheet draft as that approval.

```text
Read docs/team-setup.md and start step 1. Confirm this is a private copy before asking for company data. Ask one question at a time. Draft in chat only; do not write files or change any system.
```

Done: each definition has a reviewed source, owner, approver, and date, or a visible GAP.

## 2. Derive instructions from the definitions

Draft what the agent reads, what it may propose, and which person reviews the result. Cite each reviewed definition. Keep fixed rule IDs and the source authority in `brain/sources.md`. Flag conflicts for the source owner; do not choose a winner outside that policy.

```text
Read docs/deployment-plan-template.md. Draft step 2 instructions in chat from the reviewed definitions I provide. Cite their paths and sections. Preserve fixed rule IDs and current approval boundaries. Mark missing answers GAP. Do not write files, change permissions, connect or sync tools, send messages, or write to a CRM.
```

Done: each instruction names its source, allowed output, review owner, and unresolved gaps.

## 3. Plan access

List who may see, read, and write each resource, and who approves each action. Include the agent as a separate actor. Keep sensitive sources private and record the smallest access needed. An access proposal is not an access grant.

```text
Draft the worksheet access matrix in chat using only the actors and resources I provide. Separate visibility, read, write, and approval rights. Mark unanswered rights GAP. Do not write files, change permissions, connect or sync tools, send messages, or write to a CRM.
```

Done: every actor and resource has explicit proposed rights and an approver, or a GAP.

## 4. Plan connections

Inventory the source, destination, owner, data, direction, and proposed read or write behavior for each connection. Keep the starter's local CSV route. A live connector needs a separate activation plan and explicit authorization. Store no credentials here.

```text
Draft the worksheet connection inventory in chat from the systems I name. Cite current source authority and record direction, data scope, freshness, owner, and separate activation requirements. Mark unknowns GAP. Do not write files, change permissions, connect or sync tools, send messages, or write to a CRM.
```

Done: each proposed connection has a scope, owner, authority reference, and activation gate.

## 5. Plan validation and acceptance

Define expected results before a trial. Include missing input, stale data, conflicting sources, and unapproved changes. Plan a local trial with approved records and no live effects. Record actual results only from observed evidence; a planned check is not a pass.

The existing [eval runner](../evals/README.md) uses the signed-in Claude CLI and incurs model usage. Run it separately when authorized. The `setup-fresh-days` case checks the existing setup proposal boundary; it does not validate your connections or access.

```text
Draft validation and acceptance criteria in chat for the worksheet. Use reviewed definitions to set expected results and failure cases. Record actual results only from evidence I supply; otherwise mark GAP. Do not run trials or model evals, write files, change permissions, connect or sync tools, send messages, or write to a CRM.
```

Done: the acceptance owner records each expected and actual result, evidence, open gaps, and a dated verdict after separate trials.

## 6. Plan retirement after acceptance

Keep the current workflow until the acceptance owner approves the replacement against its criteria. Plan retention, rollback, dependencies, and a named retirement owner. Acceptance alone does not authorize deletion or disconnection.

```text
Draft retirement conditions in chat for the worksheet. Require documented acceptance first. Name the owner, dependencies, retention, rollback, and separate authorization needed for each retirement action. Leave missing evidence as GAP. Do not retire anything, write files, change permissions, connect or sync tools, send messages, or write to a CRM.
```

Done: retirement remains blocked until acceptance evidence and explicit authorization for the specific retirement action exist.
