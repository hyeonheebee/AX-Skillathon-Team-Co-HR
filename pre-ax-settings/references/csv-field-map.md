# CSV field map

Use this reference after running `scripts/parse_survey.py`. Header wording may vary; map by meaning and inspect unresolved columns instead of assuming a fixed survey form.

## Core semantics

| Semantic field | Typical Korean header cues | Required behavior |
|---|---|---|
| `name` | 이름, 성명 | Use privately; mask on participant sites |
| `organization` | 소속, 팀, 부서 | Use privately; mask on participant sites |
| `role_summary` | 주요 업무, 담당 업무 | Use as work context |
| `ai_experience` | AI 도구 사용 경험 | Use for exercise difficulty and setup |
| `preferred_track` | 참여 트랙, 희망 트랙 | Use as a signal, not an unquestionable label |
| `success_definition` | 무엇이 달라지면 성공 | Convert into completion criteria |
| `account_readiness` | GPT/Codex 접속 상태 | Convert into pre-class actions |

If a core column is absent, preserve the row, use `확인 필요`, and surface the gap in manager materials.

## Workflow-tool path

| Semantic field | Header cues | Use |
|---|---|---|
| `bottleneck` | 반복/병목 업무, 개선하고 싶은 업무 | Primary problem |
| `frequency` | 얼마나 자주 | Priority and expected gain |
| `time_cost` | 1회 수행 시간 | Baseline |
| `process_types` | 주로 다루는 프로세스 | Workflow steps |
| `pain_reasons` | 힘든 이유 | Design constraints |
| `tools` | 파일/도구 | Integration and setup |
| `workflow_sample` | 실습 자료 | Prototype input |
| `workflow_manual_minutes` | 손으로 처리 시간 | Baseline |

## Dashboard path

| Semantic field | Header cues | Use |
|---|---|---|
| `desired_dashboard` | 어떤 대시보드 | Primary output |
| `dashboard_purpose` | 무엇을 확인 | Decision question |
| `current_dashboard_process` | 현재 어떻게 확인 | Current-state flow |
| `data_locations` | 데이터가 어디에 | Source inventory |
| `audience` | 누가 보는가 | Information density and permissions |
| `update_cycle` | 업데이트 주기 | Refresh design |
| `usage_plan` | 완성 후 활용 | Operating context |
| `dashboard_sample` | 데이터 샘플 | Prototype input |
| `dashboard_manual_minutes` | 현황 수작업 시간 | Baseline |

## Shared preparation fields

| Semantic field | Header cues | Use |
|---|---|---|
| `concerns` | 걱정되는 점 | Instructor intervention |
| `requested_tools` | 다뤄줬으면 하는 AI 도구 | Curriculum emphasis |

## Fallback precedence

Choose a participant's primary track in this order:

1. An explicit preferred track containing dashboard or workflow/tool language
2. Populated dashboard-purpose or desired-dashboard fields
3. Populated bottleneck/process fields
4. `needs-review`

Choose the primary problem:

- dashboard: desired dashboard → dashboard purpose → current process → role summary
- workflow-tool: bottleneck → pain reason → role summary → success definition

Choose prototype data:

- use the relevant supplied sample only after checking for sensitive data
- otherwise create a small synthetic sample and label it `예시/Mock 데이터`
- never fabricate a business fact and present it as survey evidence

## CSV handling

- Preserve the source file and its row order.
- Decode in this order: UTF-8 with BOM, UTF-8, CP949.
- Remove completely empty rows.
- Remove exact duplicate rows only; disclose the number removed.
- Do not merge people merely because names or organizations match.
- Use stable IDs `p001`, `p002`, and so on.
- Do not copy the source CSV into the deliverables directory.
