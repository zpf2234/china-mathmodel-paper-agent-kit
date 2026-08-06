#!/usr/bin/env python3
"""Verify that the language gate accepts clean prose and rejects known production traces."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


CASES = {
    "calculation_scope": "模型假设与计算口径如下。",
    "answer_label": "本文的回答可概括为三个方面。",
    "rubric_meta": "该处理满足问题一对模型建立和可计算性的要求。",
    "reader_explanation": "前者回答能否形成，后者回答是否需要修正。",
    "preset_conclusion": "不因材料名称或条纹振幅大小预设结论。",
    "definition_navigation": "在表中列出的局部多项式系数在首次出现处定义。",
    "appendix_navigation": "完整程序见附录。",
    "file_trace": "具体结果见附件中的 CSV 文件。",
    "ai_trace": "本文使用 AI 提示词辅助生成。",
}

EXPECTED_PATTERNS = {"preset_conclusion": "reader_explanation"}


def write_fixture(root: Path, body: str) -> None:
    paper = root / "论文/论文.tex"
    paper.parent.mkdir(parents=True, exist_ok=True)
    paper.write_text(body, encoding="utf-8")


def run_case(script: Path, root: Path, expected_pass: bool, expected_pattern: str | None = None) -> dict:
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(root), "--files", "论文/论文.tex"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    report_path = root / "审查/section-chain/language-audit.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    patterns = {
        finding.get("pattern")
        for record in report.get("records", [])
        for finding in record.get("hard", [])
        if isinstance(finding, dict)
    }
    actual_pass = completed.returncode == 0 and report.get("pass") is True
    pattern_pass = expected_pattern is None or expected_pattern in patterns
    return {
        "expected_pass": expected_pass,
        "actual_pass": actual_pass,
        "expected_pattern": expected_pattern,
        "patterns": sorted(value for value in patterns if isinstance(value, str)),
        "pass": actual_pass == expected_pass and pattern_pass,
        "returncode": completed.returncode,
        "hard_count": report.get("hard_count"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="审查/language-audit-selftest.json")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    skills_root = Path(__file__).resolve().parents[2]
    script = skills_root / "cumcm-language-audit/scripts/audit_language.py"
    results: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="cumcm-language-selftest-") as tmp:
        base = Path(tmp)
        clean_root = base / "clean"
        write_fixture(clean_root, "由边界条件可得厚度估计为 7.46 微米，窗口扰动下变化不超过 0.09 微米。")
        results["clean"] = run_case(script, clean_root, True)
        for name, body in CASES.items():
            case_root = base / name
            write_fixture(case_root, body)
            results[name] = run_case(script, case_root, False, EXPECTED_PATTERNS.get(name, name))

    result = {
        "schema_version": 1,
        "pass": all(item["pass"] for item in results.values()),
        "case_count": len(results),
        "cases": results,
    }
    if not args.no_write:
        output = Path(args.root).resolve() / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "case_count": len(results)}, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
