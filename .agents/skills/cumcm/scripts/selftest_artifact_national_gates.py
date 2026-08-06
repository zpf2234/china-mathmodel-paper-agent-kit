#!/usr/bin/env python3
"""Focused regressions for figure census, track isolation, score/PDF binding and provenance."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("audit_artifacts", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load audit_artifacts")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    skills = Path(__file__).resolve().parents[2]
    audit = load_module(skills / "cumcm-review/scripts/audit_artifacts.py")
    cases: dict[str, bool] = {}
    tex = r"""
    \begin{figure}[H]\includegraphics{a.pdf}\caption{A}\label{fig:a}\end{figure}
    \begin{figure}\includegraphics{b.pdf}\caption{B}\end{figure}
    """
    figures = audit.tex_formal_figures(tex)
    cases["tex_census_requires_caption_label"] = len(figures) == 1 and figures[0]["label"] == "fig:a"
    cases["percentile_interpolates"] = audit.percentile([21, 22, 23], 0.25) == 21.5

    with tempfile.TemporaryDirectory(prefix="cumcm-artifact-gates-") as tmp:
        root = Path(tmp)
        (root / "论文").mkdir()
        (root / "审查/provenance").mkdir(parents=True)
        pdf = root / "论文/论文.pdf"
        pdf.write_bytes(b"PDF-A")
        evidence = root / "evidence.txt"
        evidence.write_text("ok", encoding="utf-8")
        dimensions = {
            name: {"score": 5 if name in {"可视表达", "提交就绪", "题意与口径"} else 4,
                   "evidence": ["evidence.txt"]}
            for name in audit.SCORE_DIMENSIONS
        }
        # 3*5 + 9*4 = 51; raise two dimensions to reach 57.
        for name in ("数据理解", "模型适配", "数学严谨", "求解实现", "验证强度", "结果价值"):
            dimensions[name]["score"] = 5
        total = sum(item["score"] for item in dimensions.values())
        card = {
            "verdict": "PASS_NATIONAL_FIRST_CANDIDATE", "hard_gates_pass": True,
            "pdf_binding": {"path": "论文/论文.pdf", "sha256": sha256(pdf)},
            "dimensions": dimensions, "total": total, "p0_findings": [], "p1_findings": [],
        }
        card_path = root / "审查/评分卡.json"
        card_path.write_text(json.dumps(card, ensure_ascii=False), encoding="utf-8")
        cases["valid_score_and_pdf_binding"] = not audit.validate_national_scorecard(root, card_path, pdf, sha256(pdf))
        pdf.write_bytes(b"PDF-B")
        binding_errors = audit.validate_national_scorecard(root, card_path, pdf, sha256(pdf))
        cases["changed_pdf_breaks_binding"] = any("SHA-256" in item for item in binding_errors)

        vector = root / "论文/a.pdf"
        vector.write_bytes(b"VECTOR")
        source = root / "source.csv"
        source.write_bytes(b"x,y\n1,2\n")
        manifest = root / "审查/provenance/a.json"
        manifest.write_text(json.dumps({
            "status": "VERIFIED", "output": "论文/a.pdf", "output_sha256": sha256(vector),
            "inputs": [{"path": "source.csv", "role": "source_data", "sha256": sha256(source)}],
        }), encoding="utf-8")
        item = {"vector_output": "论文/a.pdf", "generation": {"provenance_manifest": "审查/provenance/a.json"}}
        cases["valid_provenance_hash"] = not audit.validate_provenance(root, item)
        vector.write_bytes(b"CHANGED")
        cases["changed_vector_breaks_provenance"] = any(
            "SHA-256" in value for value in audit.validate_provenance(root, item)
        )

    result = {"pass": all(cases.values()), "cases": cases}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
