#!/usr/bin/env python3
"""Normalize one AX training pre-survey CSV into a stable JSON contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


FIELD_RULES = {
    "timestamp": ["타임스탬프", "timestamp", "제출 시간"],
    "name": ["이름", "성명", "name"],
    "organization": ["소속 팀/부서", "소속", "부서", "organization"],
    "role_summary": ["주요 업무를", "주요 업무", "담당 업무", "role"],
    "ai_experience": ["평소 ai 도구 사용 경험", "ai 도구 사용 경험", "ai 경험"],
    "preferred_track": ["어떤 트랙으로", "참여 트랙", "희망 트랙"],
    "bottleneck": ["나의 업무 중 단 하나", "가장 개선하고 싶은", "반복/병목 업무"],
    "frequency": ["위 업무를 얼마나 자주", "업무 빈도", "수행 빈도"],
    "time_cost": ["1회 수행에", "1회 소요", "소요 시간"],
    "process_types": ["해당 업무에서 주로 다루는 프로세스", "업무 프로세스"],
    "pain_reasons": ["해당 업무가 힘든 이유", "힘든 이유", "병목 이유"],
    "tools": ["해당 업무에 쓰는 파일/도구", "사용 파일/도구", "사용 도구"],
    "workflow_sample": ["실습때 사용해 볼 자료", "실습 때 사용해 볼 자료"],
    "workflow_manual_minutes": ["위 자료를 손으로 처리", "자료를 손으로 처리"],
    "desired_dashboard": ["어떤 대시보드를 만들고", "원하는 대시보드"],
    "dashboard_purpose": ["그 대시보드는 어떤 것을 확인", "대시보드 목적"],
    "current_dashboard_process": ["위의 목적을 확인하기 위해 현재는", "현재 확인 방법"],
    "data_locations": ["대시보드에서 보여주고 싶은 데이터", "데이터 위치"],
    "audience": ["대시보드는 누가 보게", "대시보드 사용자", "대시보드 대상"],
    "update_cycle": ["대시보드 업데이트는", "업데이트 주기"],
    "usage_plan": ["완성 후 어떻게 활용", "활용 계획"],
    "dashboard_sample": ["대시보드에 넣고 싶은 데이터 샘플", "대시보드 데이터 샘플"],
    "dashboard_manual_minutes": ["위 데이터로 현황을 손으로", "현황을 손으로 정리"],
    "success_definition": ["해당 실습 시리즈가 끝났을 때", "성공일까요", "성공 기준"],
    "concerns": ["세션 참여 시 걱정", "걱정되는 점", "우려 사항"],
    "requested_tools": ["세션에서 다뤄줬으면 하는 ai 도구", "희망 ai 도구"],
    "account_readiness": ["세션 당일 사용할 ai 도구", "접속 상태", "계정 준비"],
}


def compact(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalized_header(value: str) -> str:
    return re.sub(r"[\s?()/_\-\[\]]+", "", value).lower()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], str]:
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                headers = [compact(header) for header in (reader.fieldnames or []) if header]
                if not headers:
                    raise ValueError("CSV header row is empty.")
                rows = []
                for raw in reader:
                    row = {compact(key): compact(value) for key, value in raw.items() if key}
                    if any(row.values()):
                        rows.append(row)
                return headers, rows, encoding
        except UnicodeDecodeError as exc:
            last_error = exc
    raise ValueError(f"Unable to decode CSV as utf-8-sig, utf-8, or cp949: {last_error}")


def resolve_columns(headers: Iterable[str]) -> dict[str, str]:
    header_list = list(headers)
    normalized = {header: normalized_header(header) for header in header_list}
    result: dict[str, str] = {}
    for semantic, aliases in FIELD_RULES.items():
        for alias in aliases:
            needle = normalized_header(alias)
            match = next(
                (
                    header
                    for header in header_list
                    if normalized[header] == needle or normalized[header].startswith(needle)
                ),
                None,
            )
            if match:
                result[semantic] = match
                break
    return result


def value(row: dict[str, str], columns: dict[str, str], key: str) -> str:
    return compact(row.get(columns.get(key, ""), ""))


def mask_identity(text: str) -> str:
    cleaned = compact(text)
    return f"{cleaned[0]}**" if cleaned else ""


def track_category(row: dict[str, str], columns: dict[str, str]) -> str:
    preferred = value(row, columns, "preferred_track").lower()
    dashboard_signal = " ".join(
        (
            preferred,
            value(row, columns, "desired_dashboard"),
            value(row, columns, "dashboard_purpose"),
        )
    )
    workflow_signal = " ".join(
        (
            preferred,
            value(row, columns, "bottleneck"),
            value(row, columns, "process_types"),
        )
    )
    if any(token in preferred for token in ("대시보드", "dashboard")):
        return "dashboard"
    if any(token in preferred for token in ("자동화", "반복", "워크플로", "도구", "assistant", "에이전트")):
        return "workflow-tool"
    if value(row, columns, "desired_dashboard") or value(row, columns, "dashboard_purpose"):
        return "dashboard"
    if value(row, columns, "bottleneck") or any(
        token in workflow_signal for token in ("반복", "정리", "검토", "작성", "취합", "발송")
    ):
        return "workflow-tool"
    if "대시보드" in dashboard_signal:
        return "dashboard"
    return "needs-review"


def choose_problem(row: dict[str, str], columns: dict[str, str], track: str) -> str:
    if track == "dashboard":
        choices = ("desired_dashboard", "dashboard_purpose", "current_dashboard_process", "role_summary")
    else:
        choices = ("bottleneck", "pain_reasons", "role_summary", "success_definition")
    return next((value(row, columns, key) for key in choices if value(row, columns, key)), "확인 필요")


def deduplicate(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for row in rows:
        payload = json.dumps(row, ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if digest not in seen:
            seen.add(digest)
            unique.append(row)
    return unique, len(rows) - len(unique)


def build_participant(
    row: dict[str, str], columns: dict[str, str], sequence: int
) -> dict[str, str]:
    track = track_category(row, columns)
    workflow_sample = value(row, columns, "workflow_sample")
    dashboard_sample = value(row, columns, "dashboard_sample")
    current_process = value(row, columns, "current_dashboard_process")
    if not current_process:
        current_process = value(row, columns, "process_types")
    desired_output = value(row, columns, "desired_dashboard")
    if not desired_output and track == "workflow-tool":
        desired_output = "반복 업무를 줄이는 실행 가능한 도구 또는 어시스턴트"
    if not desired_output:
        desired_output = "확인 필요"
    manual_minutes = (
        value(row, columns, "dashboard_manual_minutes")
        if track == "dashboard"
        else value(row, columns, "workflow_manual_minutes")
    )
    return {
        "participant_id": f"p{sequence:03d}",
        "name": value(row, columns, "name") or f"수강생 {sequence}",
        "organization": value(row, columns, "organization") or "소속 확인 필요",
        "masked_name": mask_identity(value(row, columns, "name") or f"수강생 {sequence}"),
        "masked_organization": mask_identity(
            value(row, columns, "organization") or "소속 확인 필요"
        ),
        "role_summary": value(row, columns, "role_summary"),
        "ai_experience": value(row, columns, "ai_experience"),
        "preferred_track": value(row, columns, "preferred_track"),
        "track_category": track,
        "problem": choose_problem(row, columns, track),
        "current_process": current_process,
        "frequency": value(row, columns, "frequency"),
        "time_cost": value(row, columns, "time_cost"),
        "manual_minutes": manual_minutes,
        "process_types": value(row, columns, "process_types"),
        "pain_reasons": value(row, columns, "pain_reasons"),
        "tools": value(row, columns, "tools"),
        "sample_data": dashboard_sample if track == "dashboard" else workflow_sample,
        "sample_data_status": "provided" if (dashboard_sample if track == "dashboard" else workflow_sample) else "missing-use-mock",
        "desired_output": desired_output,
        "dashboard_purpose": value(row, columns, "dashboard_purpose"),
        "data_locations": value(row, columns, "data_locations"),
        "audience": value(row, columns, "audience"),
        "update_cycle": value(row, columns, "update_cycle"),
        "usage_plan": value(row, columns, "usage_plan"),
        "success_definition": value(row, columns, "success_definition"),
        "concerns": value(row, columns, "concerns"),
        "requested_tools": value(row, columns, "requested_tools"),
        "account_readiness": value(row, columns, "account_readiness"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize one AX training pre-survey CSV into JSON."
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.input_csv.is_file():
        print(f"ERROR: CSV not found: {args.input_csv}", file=sys.stderr)
        return 2

    try:
        headers, raw_rows, encoding = read_csv(args.input_csv)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    rows, duplicates_removed = deduplicate(raw_rows)
    columns = resolve_columns(headers)
    participants = [build_participant(row, columns, index) for index, row in enumerate(rows, 1)]
    track_counts = dict(Counter(item["track_category"] for item in participants))
    missing_core = [
        semantic
        for semantic in ("name", "organization", "role_summary", "preferred_track", "success_definition")
        if semantic not in columns
    ]
    payload = {
        "schema_version": "1.0",
        "source": {
            "file_name": args.input_csv.name,
            "encoding": encoding,
            "header_count": len(headers),
            "headers": headers,
        },
        "metadata": {
            "raw_response_count": len(raw_rows),
            "participant_count": len(participants),
            "duplicates_removed": duplicates_removed,
            "track_counts": track_counts,
            "resolved_columns": columns,
            "missing_core_columns": missing_core,
        },
        "participants": participants,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "participant_count": len(participants),
                "track_counts": track_counts,
                "duplicates_removed": duplicates_removed,
                "missing_core_columns": missing_core,
            },
            ensure_ascii=False,
        )
    )
    return 0 if participants else 1


if __name__ == "__main__":
    raise SystemExit(main())
