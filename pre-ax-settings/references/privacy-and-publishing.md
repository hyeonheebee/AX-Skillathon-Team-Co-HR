# Privacy and publishing

## Identity masking

For every participant-facing or shared/public artifact:

- keep only the first visible character of the name and append `**`
- keep only the first visible character of the organization and append `**`
- example: `홍길동` → `홍**`, `서울AI허브` → `서**`
- if missing, use `수**` or `소**` and mark the private record as `확인 필요`

Masking is a display safeguard, not anonymization. Do not include combinations of role, raw text, unique project details, or sample records that make the person readily identifiable when broad sharing is planned.

## Content boundaries

Private manager materials may contain full names and organizations because the manager must operate the class. Participant sites and shared links must not.

Participant sites must never contain:

- full name or full organization
- another participant's ID, prompt, problem, or link
- manager materials or manager navigation
- the source CSV or raw response JSON
- real personal, account, contract, customer, or employee data
- secrets, access tokens, or private workspace URLs

Replace unsafe samples with small synthetic examples and label them.

## Publishing gate

Do not deploy because a local site exists. Publish only after an explicit user request.

Before publishing:

1. identify the requested audience: private, selected users, workspace-wide, or public
2. confirm that the manager dashboard is excluded
3. run `scripts/validate_outputs.py`
4. visually inspect every participant site
5. verify that each production URL opens the intended participant only
6. record the URL and `deployed` status in `manifest.json`
7. rerun validation so Slack drafts match the deployed links

If the user requests workspace-wide access, use the platform's workspace-wide access setting. Do not silently widen access beyond the requested audience.

## Slack gate

Drafting does not authorize sending. Keep `slack_status` as `draft_only`.

Before sending:

1. match Slack recipient to the private name and `participant_id`
2. match the personal URL from `manifest.json`
3. confirm that the URL is a participant site, not the manager site
4. show or preserve the concise final draft
5. send only after the user explicitly requests sending

Do not report a message as sent without tool evidence.
