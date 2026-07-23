#!/usr/bin/env python3
"""Validate a pre-ax-settings deliverable tree for completeness and privacy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


PROMPT_SECTIONS = ("역할", "목표", "입력", "처리", "출력", "주의", "완료")
GUARDRAIL_GROUPS = (
    ("근거", "추정", "검증", "누락"),
    ("민감", "개인정보", "비식별"),
    ("승인", "사람", "최종 판단", "최종판단"),
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate pre-ax-settings output completeness, privacy, and link mapping."
    )
    parser.add_argument("--normalized", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        normalized = load_json(args.normalized)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "errors": [f"normalized JSON 읽기 실패: {exc}"]}, ensure_ascii=False))
        return 2

    participants = normalized.get("participants", [])
    root = args.root
    required_shared = (
        root / "manager" / "manager-dashboard.html",
        root / "manager" / "cohort-summary.md",
        root / "communications" / "slack-drafts.md",
    )
    for path in required_shared:
        if not path.is_file():
            errors.append(f"필수 파일 없음: {path.relative_to(root)}")

    manifest_path = args.manifest or root / "manifest.json"
    manifest: dict = {}
    if not manifest_path.is_file():
        errors.append("필수 파일 없음: manifest.json")
    else:
        try:
            manifest = load_json(manifest_path)
        except json.JSONDecodeError as exc:
            errors.append(f"manifest.json 형식 오류: {exc}")

    manifest_rows = {
        item.get("participant_id"): item
        for item in manifest.get("participants", [])
        if isinstance(item, dict) and item.get("participant_id")
    }
    if manifest and manifest.get("participant_count") != len(participants):
        errors.append("manifest participant_count가 정규화된 응답 수와 다름")
    if manifest and manifest.get("slack_status") != "draft_only":
        warnings.append("Slack 상태가 draft_only가 아님. 실제 발송 근거를 별도로 확인할 것")

    raw_identities = []
    for participant in participants:
        for key in ("name", "organization"):
            identity = str(participant.get(key, "")).strip()
            if len(identity) >= 2 and "확인 필요" not in identity:
                raw_identities.append((participant.get("participant_id"), key, identity))

    seen_urls: set[str] = set()
    slack_copy = text(root / "communications" / "slack-drafts.md") if (root / "communications" / "slack-drafts.md").is_file() else ""

    for participant in participants:
        pid = participant.get("participant_id", "")
        base = root / "participants" / pid
        expected = {
            "brief": base / "brief.md",
            "prompt": base / "magic-prompt.md",
            "prototype": base / "prototype" / "index.html",
        }
        for label, path in expected.items():
            if not path.is_file():
                errors.append(f"{pid} 필수 파일 없음: {path.relative_to(root)}")

        prompt_path = expected["prompt"]
        if prompt_path.is_file():
            prompt = text(prompt_path)
            for section in PROMPT_SECTIONS:
                if section not in prompt:
                    errors.append(f"{pid} 마법의 프롬프트에 '{section}' 섹션이 없음")
            for group in GUARDRAIL_GROUPS:
                if not any(term in prompt for term in group):
                    errors.append(f"{pid} 마법의 프롬프트 가드레일 누락: {'/'.join(group)}")

        prototype_path = expected["prototype"]
        if prototype_path.is_file():
            prototype = text(prototype_path)
            masked_name = str(participant.get("masked_name", ""))
            masked_org = str(participant.get("masked_organization", ""))
            if masked_name and masked_name not in prototype:
                errors.append(f"{pid} 사이트에 마스킹된 이름이 없음")
            if masked_org and masked_org not in prototype:
                errors.append(f"{pid} 사이트에 마스킹된 소속이 없음")
            for owner_pid, key, identity in raw_identities:
                if identity in prototype:
                    errors.append(
                        f"{pid} 사이트에 원문 {key} 노출: {owner_pid}의 '{identity}'"
                    )
            for other in participants:
                other_pid = other.get("participant_id", "")
                if other_pid and other_pid != pid and re.search(rf"\b{re.escape(other_pid)}\b", prototype):
                    errors.append(f"{pid} 사이트에 다른 수강생 ID 노출: {other_pid}")
            if re.search(r"manager[-_ ]?dashboard|운영\s*대시보드", prototype, re.IGNORECASE):
                errors.append(f"{pid} 사이트에 교육매니저 대시보드 참조가 있음")

        row = manifest_rows.get(pid)
        if not row:
            errors.append(f"manifest에 {pid} 항목 없음")
            continue
        expected_path = f"participants/{pid}/prototype/index.html"
        if row.get("site_path") != expected_path:
            errors.append(f"manifest의 {pid} site_path가 예상 경로와 다름")
        if row.get("masked_name") != participant.get("masked_name"):
            errors.append(f"manifest의 {pid} masked_name 불일치")
        if row.get("masked_organization") != participant.get("masked_organization"):
            errors.append(f"manifest의 {pid} masked_organization 불일치")
        site_url = str(row.get("site_url", "")).strip()
        if site_url:
            if not valid_url(site_url):
                errors.append(f"manifest의 {pid} site_url이 유효한 http(s) URL이 아님")
            if site_url in seen_urls:
                errors.append(f"중복 participant site_url: {site_url}")
            seen_urls.add(site_url)
            if site_url not in slack_copy:
                errors.append(f"{pid} Slack 초안에 개인 사이트 URL이 없음")
        elif expected_path not in slack_copy and pid not in slack_copy:
            warnings.append(f"{pid} Slack 초안에 로컬 경로나 participant_id가 없음")
        full_name = str(participant.get("name", "")).strip()
        if full_name and full_name not in slack_copy:
            warnings.append(f"{pid} Slack 초안에서 수신자 이름을 확인할 수 없음")

    if len(manifest_rows) != len(participants):
        errors.append("manifest participant 항목 수가 정규화된 응답 수와 다름")

    result = {
        "ok": not errors,
        "participant_count": len(participants),
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "required_files": "pass" if not any("필수 파일" in item for item in errors) else "fail",
            "prompt_guardrails": "pass" if not any("프롬프트" in item or "가드레일" in item for item in errors) else "fail",
            "privacy_and_isolation": "pass" if not any("사이트에" in item for item in errors) else "fail",
            "manifest_and_links": "pass" if not any("manifest" in item or "site_url" in item or "URL" in item for item in errors) else "fail",
            "slack_status": manifest.get("slack_status", "unknown") if manifest else "unknown",
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
