---
name: pre-ax-settings
description: "Turn one AX training pre-survey CSV into a complete pre-class preparation package: normalized cohort analysis, education-manager guidance, per-participant problem definitions, setup checklists, tailored magic prompts, working prototype drafts, isolated participant site materials, and Slack DM drafts. Use when planning or operating an AX/AI workshop from registration or pre-survey responses in CSV format, especially when each learner needs a personalized deliverable and privacy-safe sharing."
---

# Pre-AX Settings

## Outcome

Convert exactly one pre-survey CSV into a complete, reviewable workshop package. Produce both the education manager's operating view and one isolated participant package per valid response. Keep generation deterministic where possible, expose assumptions, and use synthetic examples when respondents did not provide usable data.

## Required Input

Accept one `.csv` file as the only required input. Do not require a separate brief, roster, template, or sample-data file.

If schedule, venue, instructor, brand, or publishing details are missing, use visible placeholders or mark them `확인 필요`. Do not block the analysis.

Read [references/csv-field-map.md](references/csv-field-map.md) before interpreting the CSV. Normalize it first:

```bash
python3 scripts/parse_survey.py "/absolute/path/to/pre-survey.csv" \
  --output "/absolute/path/to/work/normalized.json"
```

The parser uses only the Python standard library. Do not install packages merely to read the CSV.

## Workflow

### 1. Inspect and normalize

Confirm encoding, headers, valid response count, duplicate removal, and missing core fields. Treat each non-empty, non-duplicate row as one participant.

Use `participant_id` as the stable key. Never use the participant's name as a filename, route, or site identifier.

### 2. Analyze the cohort

Summarize:

- participant count and track mix
- AI experience and account-readiness distribution
- repeated bottlenecks and desired dashboards
- available tools, sample data, and data locations
- concerns, missing information, and instructor interventions
- pre-class risks that must be resolved before hands-on work

Separate facts from the CSV, reasonable inferences, and unanswered questions.

### 3. Build the pre-class setup plan

Create D-3, D-2, D-1, session-day, and post-session checklists. At minimum cover:

- GPT/Codex login and permissions
- browser, download, and local-file access
- sample-data availability and safe substitutes
- sensitive-data removal
- expected artifact for each participant
- instructor fallback when an account, file, or tool fails

Do not claim that an account, integration, or permission is ready unless the CSV supports it.

### 4. Design one participant package per response

For each participant, create:

1. a one-sentence problem definition
2. current-state pain and target outcome
3. a tailored pre-setting checklist
4. missing inputs and questions to confirm
5. a task-specific magic prompt
6. a runnable prototype draft
7. a workshop exercise path
8. validation criteria and next development ideas

Choose the primary artifact:

- `dashboard`: create an interactive, single-page dashboard using safe mock data when necessary.
- `workflow-tool`: create an interactive helper, review assistant, checklist, generator, or task widget that matches the bottleneck.
- `needs-review`: choose the smallest credible interactive prototype and label the assumption.

Do not return only an idea, report, or wireframe when the user asked for a result. Produce a locally openable artifact.

### 5. Write the magic prompt

Read [references/prompt-blueprints.md](references/prompt-blueprints.md). Tailor the prompt to the respondent rather than substituting names into a generic prompt.

Every prompt must define role, objective, accepted input, processing rules, output contract, evidence/uncertainty rules, privacy limits, human-approval gates, and completion criteria. Never invent missing business data.

### 6. Build the manager package

Follow [references/output-contract.md](references/output-contract.md). The manager dashboard must make it possible to:

- see what problems participants brought
- compare tracks, readiness, risks, and expected outputs
- review every participant's setup and magic prompt
- run the program from preparation through follow-up
- identify what must be taught, confirmed, or warned about

The manager dashboard may contain identifiable information when it remains private. Participant sites may not.

### 7. Prepare participant sites

Use [assets/site-shell/participant.html](assets/site-shell/participant.html) as the minimum standalone shell. Each participant site must contain only that participant's content.

Mask the displayed name and organization before any shared or public build. Keep only the first visible character and replace the remainder with `**`, for example `홍**` and `서**`.

Never include:

- another participant's content or navigation
- the manager dashboard or a route to it
- raw survey rows
- an unmasked full name or organization
- sensitive sample data

Read [references/privacy-and-publishing.md](references/privacy-and-publishing.md) before preparing any shared artifact.

### 8. Draft communications

Prepare one short Slack DM draft per participant, matched by `participant_id` to the correct personal link. Default to draft-only status.

Use this intent:

> 내일 만들 프로토타입을 미리 보고 원하는 방향인지 확인해 주세요. 부족한 부분과 더 발전시킬 방향도 함께 생각해 보면 좋겠습니다.

Do not send messages unless the user separately and explicitly asks to send them. If sending is authorized, use the Slack workflow. Use Computer Use only when the user explicitly requests it.

### 9. Publish only when requested

Local artifact creation does not authorize deployment. If the user explicitly asks to publish:

1. follow the Sites building and hosting skills
2. confirm or use the access level specified by the user
3. deploy separate participant sites or strictly isolated participant routes
4. exclude manager materials
5. validate masking and link mapping before sharing

Treat every deployment URL as production.

### 10. Delegate only when requested

If the user explicitly asks for subagents or one agent per participant, delegate each participant package as an independent bounded task. Give every agent only the normalized row and shared output contract it needs. The primary agent must reconcile style, privacy, and validation across all results.

Do not delegate merely because multiple participants exist.

### 11. Validate and report

Create `manifest.json`, then run:

```bash
python3 scripts/validate_outputs.py \
  --normalized "/absolute/path/to/work/normalized.json" \
  --root "/absolute/path/to/deliverables"
```

Fix every reported error before declaring completion. Review warnings and disclose any accepted limitation.

Report:

- number of responses and participant packages
- track breakdown
- created file and site locations
- privacy/route-isolation result
- local, draft, or deployed status
- missing facts the manager must confirm
- whether Slack messages remain drafts or were explicitly sent

## Operating Rules

- Preserve the source CSV; never overwrite it.
- Do not copy the source CSV into the deliverables folder.
- Use full names only in private manager material and direct-message drafts.
- Use masked identity in participant sites and shared/public artifacts.
- Use mock data when usable sample data is absent, and label it as mock data.
- Never expose secrets, personal data, or private URLs in prompts or prototypes.
- Keep human review for consequential decisions, external messages, contract judgments, and final publication.
- Prefer a simple working prototype over a complex non-runnable concept.
- Do not state that publishing or sending succeeded without tool evidence.
