# Output contract

Create this exact minimum structure:

```text
deliverables/
├── manifest.json
├── manager/
│   ├── manager-dashboard.html
│   └── cohort-summary.md
├── participants/
│   └── p001/
│       ├── brief.md
│       ├── magic-prompt.md
│       └── prototype/
│           └── index.html
└── communications/
    └── slack-drafts.md
```

Repeat the participant directory for every normalized participant.

## Manager dashboard

Make `manager-dashboard.html` locally openable and self-contained. Include:

- cohort summary cards
- track and readiness breakdown
- problem themes and bottlenecks
- participant table/cards with identifiable private context
- pre-class D-3, D-2, D-1, day-of, and follow-up plan
- curriculum flow from problem definition to prototype review
- required instructor explanations
- missing facts, risks, privacy rules, and fallback plans
- access to each participant's private brief and prompt

Do not put manager content into participant sites.

## Cohort summary

Make `cohort-summary.md` a concise operating brief:

1. source facts
2. inferences
3. questions to confirm
4. readiness risks
5. instructional strategy
6. success measures

## Participant brief

Each `brief.md` must include:

1. participant ID and private identity
2. survey evidence
3. one-sentence problem definition
4. current state and pain
5. target artifact
6. pre-setting checklist
7. missing inputs/questions
8. 60–120 minute workshop path
9. acceptance tests
10. next development ideas

## Magic prompt

Each `magic-prompt.md` must be directly reusable. Include explicit sections for:

- 역할
- 목표
- 입력
- 처리 규칙
- 출력 형식
- 근거·추정·누락 처리
- 개인정보·민감정보
- 사람 승인 또는 최종 판단
- 금지/주의사항
- 완료 기준

## Prototype

Each `prototype/index.html` must:

- open without a build step
- visibly identify only `masked_name` and `masked_organization`
- offer at least one meaningful interaction
- match the participant's requested task
- label mock data
- show a next-step or validation state
- avoid external dependencies unless the environment requires them

## Slack drafts

Create one section per participant. Keep messages short and connect the correct link:

```text
## p001 — [private recipient name]
Status: DRAFT — NOT SENT
Link: [participant-specific URL or local placeholder]

[message]
```

## Manifest

Use:

```json
{
  "schema_version": "1.0",
  "skill": "pre-ax-settings",
  "participant_count": 1,
  "manager_dashboard": "manager/manager-dashboard.html",
  "slack_status": "draft_only",
  "participants": [
    {
      "participant_id": "p001",
      "masked_name": "홍**",
      "masked_organization": "서**",
      "site_path": "participants/p001/prototype/index.html",
      "site_url": "",
      "publish_status": "local_only"
    }
  ]
}
```

Keep `site_url` empty until a production deployment succeeds. Valid `publish_status` values are `local_only`, `saved`, and `deployed`.
