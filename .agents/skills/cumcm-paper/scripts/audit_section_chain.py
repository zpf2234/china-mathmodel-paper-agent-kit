#!/usr/bin/env python3
"""Validate CUMCM section-chain manifest and stage gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_STAGES = [
    "outline",
    "restatement",
    "analysis",
    "assumptions",
    "notation",
    "model-writing",
    "results-validation",
    "evaluation",
    "references",
    "abstract",
    "language-audit",
]
OPTIONAL_STAGES = ["appendix"]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_gate(root: Path, stage: str, spec: dict) -> list[str]:
    errors: list[str] = []
    gate_rel = spec.get("gate")
    if not gate_rel:
        return [f"{stage}: missing gate path"]
    gate_path = root / gate_rel
    if not gate_path.exists():
        return [f"{stage}: gate not found: {gate_rel}"]
    try:
        gate = read_json(gate_path)
    except Exception as exc:  # noqa: BLE001
        return [f"{stage}: invalid gate JSON: {exc}"]
    if gate.get("schema_version") != 1:
        errors.append(f"{stage}: gate schema_version must be 1")
    if gate.get("stage") != stage:
        errors.append(f"{stage}: gate stage mismatch")
    if gate.get("status") != "pass":
        errors.append(f"{stage}: status is not pass")
    if gate.get("blocking_issues"):
        errors.append(f"{stage}: blocking_issues is not empty")
    checks = gate.get("checks", [])
    if not checks:
        errors.append(f"{stage}: no checks recorded")
    for check in checks:
        if not check.get("id") or check.get("pass") is not True or not check.get("evidence"):
            errors.append(f"{stage}: incomplete or failed check: {check.get('id', '<missing>')}")
    source_files = spec.get("source_files", gate.get("source_files", []))
    if stage not in {"outline", "language-audit"} and not source_files:
        errors.append(f"{stage}: no source_files recorded")
    for item in source_files:
        if not (root / item).exists():
            errors.append(f"{stage}: source file not found: {item}")
    return errors


def validate_cross_audit(root: Path, kind: str) -> list[str]:
    """Require a passing, current automatic audit for each used visual family."""
    errors: list[str] = []
    report_rel = f"审查/{kind}-style-audit.json"
    registry_rel = f"审查/{kind}-registry.json"
    report_path = root / report_rel
    registry_path = root / registry_rel
    if not registry_path.exists():
        errors.append(f"{kind}: registry not found: {registry_rel}")
        return errors
    if not report_path.exists():
        errors.append(f"{kind}: automatic style audit report not found: {report_rel}")
        return errors
    try:
        report = read_json(report_path)
    except Exception as exc:  # noqa: BLE001
        return [f"{kind}: invalid automatic style audit report: {exc}"]
    if report.get("schema_version") != 1:
        errors.append(f"{kind}: style audit schema_version must be 1")
    if report.get("pass") is not True:
        errors.append(f"{kind}: automatic style audit did not pass")
    if report.get("registry") != registry_rel:
        errors.append(f"{kind}: style audit registry mismatch")
    count_key = "figure_count" if kind == "figure" else "diagram_count"
    if not isinstance(report.get(count_key), int) or report.get(count_key) < 1:
        errors.append(f"{kind}: style audit contains no checked visuals")
    if report_path.stat().st_mtime < registry_path.stat().st_mtime:
        errors.append(f"{kind}: style audit is older than its registry")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", default="审查/section-chain/manifest.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = root / args.manifest
    errors: list[str] = []
    if not manifest_path.exists():
        errors.append(f"manifest not found: {args.manifest}")
        manifest = {}
    else:
        try:
            manifest = read_json(manifest_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid manifest JSON: {exc}")
            manifest = {}

    if manifest.get("schema_version") != 1:
        errors.append("manifest schema_version must be 1")
    if not manifest.get("question_ids"):
        errors.append("manifest question_ids is empty")
    stages = manifest.get("stages", {})
    for stage in REQUIRED_STAGES:
        spec = stages.get(stage)
        if not spec:
            errors.append(f"missing stage: {stage}")
            continue
        errors.extend(validate_gate(root, stage, spec))
    for stage in OPTIONAL_STAGES:
        spec = stages.get(stage)
        if spec and spec.get("applicable", True) is not False:
            errors.extend(validate_gate(root, stage, spec))

    cross = manifest.get("cross_cutting", {})
    for flag, stage in (("figures_used", "figures"), ("diagrams_used", "diagrams")):
        if cross.get(flag):
            spec = stages.get(stage, {"gate": f"审查/section-chain/gates/{stage}.json"})
            errors.extend(validate_gate(root, stage, spec))
            kind = "figure" if stage == "figures" else "diagram"
            errors.extend(validate_cross_audit(root, kind))

    auto_language = root / "审查" / "section-chain" / "language-audit.json"
    if not auto_language.exists():
        errors.append("automatic language audit report not found")
    else:
        try:
            if read_json(auto_language).get("pass") is not True:
                errors.append("automatic language audit did not pass")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid automatic language audit report: {exc}")

    result = {
        "schema_version": 1,
        "pass": not errors,
        "manifest": args.manifest,
        "required_stages": REQUIRED_STAGES,
        "optional_stages": OPTIONAL_STAGES,
        "errors": errors,
    }
    out_dir = root / "审查" / "section-chain"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "chain-audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = ["# 章节技能链审计", "", f"- 结果：{'PASS' if result['pass'] else 'FAIL'}", ""]
    if errors:
        lines.extend(["## 阻断项", "", *[f"- {item}" for item in errors], ""])
    else:
        lines.extend(["全部阶段门禁、源文件和语言审计均已通过。", ""])
    (out_dir / "chain-audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "error_count": len(errors)}, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
