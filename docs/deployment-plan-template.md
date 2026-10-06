# Team deployment worksheet

Draft this worksheet in chat first. Save it only when the user requests a new dated file under `brain/setup/`.

Use a unique filename. If that filename exists, stop; never overwrite it. Keep instruction drafts inside the worksheet. Do not change active instructions or policy files through this worksheet.

Use a private repository or a private local copy before you record real company data. A public fork remains public. Record no credentials.

Replace an unanswered field with `GAP: <question or missing source>`. Never copy a sample value into a gap.

## Record

- Status: proposed
- Date: GAP: worksheet date
- Private location confirmed by: GAP: person and confirmation
- Preparation owner: GAP: name
- Acceptance owner: GAP: name
- Scope: GAP: account readiness and handoff workflow
- Current workflow to preserve: GAP: description and owner

This starter supports account readiness, not complete deal qualification. This worksheet approves no live action, access change, connector, sync, send, or CRM write.

## 1. Reviewed business definitions

| Definition | Reviewed source link and section | Owner | Approver and date | Open gap |
| --- | --- | --- | --- | --- |
| Customer criteria | GAP: source | GAP: owner | GAP: review | GAP: answer |
| Stages and handoff | GAP: source | GAP: owner | GAP: review | GAP: answer |
| Plays | GAP: source | GAP: owner | GAP: review | GAP: answer |
| Source authority | GAP: reviewed brain/sources.md | GAP: owner | GAP: review | GAP: answer |

### Current sources and authority

| Fact | Current authoritative source and policy reference | Owner | Read date and freshness requirement | Conflict or gap |
| --- | --- | --- | --- | --- |
| GAP: fact | GAP: source and rule ID | GAP: owner | GAP: dates | GAP: unresolved input |

The worksheet does not replace `brain/sources.md`. Preserve its conflict rules and report unresolved values to the source owner.

## 2. Instruction drafts

| Draft instruction | Reviewed definition references | Files to read | Allowed proposed output | Review owner | Gap |
| --- | --- | --- | --- | --- | --- |
| GAP: instruction | GAP: links and sections | GAP: paths | GAP: output | GAP: owner | GAP: answer |

- Fixed rule IDs and approval boundaries preserved: GAP: references and review
- Proposed instruction text: GAP: draft supported by reviewed definitions
- Permission to activate instructions: none; separate exact-text approval is required

## 3. Proposed access matrix

| Actor, including agent | Resource | Visibility | Read | Write | Approval right and action | Grant owner | Gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GAP: actor | GAP: resource | GAP: audience | GAP: right | GAP: right | GAP: boundary | GAP: owner | GAP: answer |

This matrix changes no permissions. Record the required authorization separately from the proposed rights.

## 4. Proposed connection inventory

| Source → destination | Owner | Data scope | Direction and read/write behavior | Authority reference | Freshness | Activation requirements | Gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GAP: systems | GAP: owner | GAP: fields | GAP: behavior | GAP: policy | GAP: age limit | GAP: separate activation plan and authorization | GAP: answer |

- Starter read path: local CSV exports
- Live activation: not authorized by this worksheet
- Credential handling: GAP: external secret storage reference, never a credential value

## 5. Validation and acceptance

| Case | Reviewed definition | Expected result | Actual observed result | Evidence and date | Pass/fail or not run | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| Normal account handoff | GAP: reference | GAP: expected | GAP: not run | GAP: evidence | not run | GAP: owner |
| Missing input | GAP: reference | GAP: expected | GAP: not run | GAP: evidence | not run | GAP: owner |
| Stale source | GAP: reference | GAP: expected | GAP: not run | GAP: evidence | not run | GAP: owner |
| Conflicting sources | GAP: reference | GAP: expected | GAP: not run | GAP: evidence | not run | GAP: owner |
| Unapproved change | GAP: reference | GAP: expected | GAP: not run | GAP: evidence | not run | GAP: owner |

- Trial scope and separate authorization: GAP: approved local inputs and actions
- Acceptance criteria: GAP: measurable required results
- Open failures and gaps: GAP: findings
- Acceptance verdict, owner, and date: GAP: not accepted

No planned check counts as observed evidence. Model evals use Claude CLI and incur model usage; authorize them separately.

## 6. Retirement conditions

| Existing item | Retirement owner | Acceptance evidence required | Dependencies and retention | Rollback plan | Specific authorization | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GAP: workflow or record | GAP: owner | GAP: accepted results | GAP: dependencies | GAP: recovery steps | GAP: action approval | blocked |

Keep the existing workflow until documented acceptance. Retire nothing until the owner has explicit authorization for that action.

See the [team setup guide](./team-setup.md) for the six prompts.
