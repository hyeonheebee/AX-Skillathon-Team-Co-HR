# Prompt blueprints

Build each magic prompt from the participant's actual problem, inputs, tools, audience, and success definition. Do not merely replace a name in a generic template.

## Shared prompt skeleton

```markdown
# [업무명] 실행 프롬프트

## 역할
당신은 [업무 맥락]을 지원하는 [분석가/운영 어시스턴트/검토자]입니다.

## 목표
[사용자가 확인하거나 완성해야 하는 결과]를 만듭니다.

## 입력
- 필수: [...]
- 선택: [...]
- 입력이 없거나 불완전할 때: [...]

## 처리 규칙
1. [...]
2. [...]
3. 사실, 추정, 확인 필요를 구분합니다.

## 출력 형식
[정확한 섹션, 표, 카드, JSON, 초안 형식]

## 근거·추정·누락 처리
- 입력에서 확인된 내용만 사실로 표시합니다.
- 추정은 `추정`으로 표시하고 이유를 씁니다.
- 누락값은 만들지 말고 `확인 필요`로 남깁니다.

## 개인정보·민감정보
- [...]

## 사람 승인
- 외부 전송, 최종 판단, 계약/정책 판단은 사람이 승인합니다.

## 금지/주의사항
- [...]

## 완료 기준
- [...]
```

## Dashboard prompt

Define:

- the decision question the dashboard answers
- source table or synthetic-data schema
- KPI formulas and units
- filters and time grain
- missing/outlier treatment
- empty, loading, and error states
- audience and refresh cadence
- a visible `예시/Mock 데이터` label when appropriate

Require the output to include:

1. KPI summary
2. trend or comparison
3. exception/attention list
4. filter controls
5. data-quality note
6. recommended next action

Do not imply live data when the prototype uses static or mock data.

## Workflow-tool prompt

Define:

- trigger and accepted input
- step-by-step transformation
- templates or policies to apply
- ambiguous cases and stop conditions
- human-approval gate
- export or copy-ready output
- history/audit information if consequential

Require the output to include:

1. input summary
2. processed result
3. warnings and missing information
4. evidence or rule used
5. a human-review checklist
6. the next action

## Review or contract assistant prompt

Keep the tool assistive, not authoritative. Require:

- clause or source evidence
- risk label with rationale
- alternative wording clearly marked as a draft
- unanswered questions
- explicit final review by a responsible person

Never claim legal certainty or auto-approve a consequential decision.

## Prompt quality test

Before saving, confirm:

- a second person could run it without oral explanation
- the output format is concrete
- missing data cannot silently become invented facts
- privacy limits are visible
- an approval gate exists where consequences leave the prototype
- completion is objectively testable
