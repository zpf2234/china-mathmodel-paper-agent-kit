#!/usr/bin/env python3
"""Run isolated positive and negative regression cases for visual audit scripts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_placeholder(path: Path, content: str = "test") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_case(script: Path, root: Path, expected_pass: bool, *extra_args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(root), *extra_args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    actual_pass = completed.returncode == 0
    return {
        "expected_pass": expected_pass,
        "actual_pass": actual_pass,
        "pass": actual_pass == expected_pass,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def valid_figure_registry() -> dict:
    return {
        "schema_version": 1,
        "figures": [
            {
                "id": "fig-1",
                "category": "time_series",
                "purpose": "证明估计曲线在稳定区间内收敛",
                "claim_ids": ["C-Q1-01"],
                "source_data": ["求解/q1/result.csv"],
                "generator": "求解/q1/plot.py",
                "vector_output": "论文/figures/q1.pdf",
                "insert_width_mm": 120,
                "final_min_font_pt": 8.5,
                "generation": {
                    "mode": "script",
                    "renderer": "matplotlib",
                    "tool": "plot.py",
                    "spec_path": "求解/q1/plot.py",
                    "provenance_manifest": "审查/provenance/q1.json",
                },
                "vector_audit": {"true_vector": True, "aspect_ratio_distortion": 0.0},
                "visual_review": {
                    "actual_size_render": "审查/renders/q1-actual.png",
                    "full_page_render": "审查/renders/q1-page.png",
                    "thumbnail_render": "审查/renders/q1-thumb.png",
                    "grayscale_render": "审查/renders/q1-gray.png",
                    "publication_ready": True,
                },
                "style": {
                    "background": "white",
                    "color_count": 3,
                    "colorblind_safe": True,
                    "data_geometry_untouched": True,
                    "units_complete": True,
                    "final_page_checked": True,
                    "grayscale_pass": True,
                    "title_inside": False,
                    "decorative_effects": False,
                    "legend_occludes_data": False,
                    "default_software_theme": False,
                    "manual_data_point_editing": False,
                },
                "role_specific_checks": [
                    {"id": "sampling_order", "pass": True, "evidence": "按原始采样顺序绘制"}
                ],
            }
        ],
    }


def valid_layout() -> dict:
    checks = {
        name: True
        for name in (
            "objects_inside_canvas",
            "node_text_embedded",
            "text_inside_parent",
            "node_lines_max_2",
            "uniform_node_text_style",
            "annotation_anchors",
            "arrow_endpoints_on_node_boundary",
            "arrowheads_outside_node_interior",
            "connection_inventory_complete",
            "non_target_crossings_zero",
            "final_render_connections_checked",
            "line_direction_semantics_complete",
            "arrow_direction_matches_meaning",
            "line_style_matches_meaning",
            "final_font_size_readable",
            "composition_balance",
        )
    }
    checks["latex_trim_required"] = False
    connection = {
        "id": "e01",
        "kind": "flow_arrow",
        "source": "更新参数",
        "target": "判定收敛",
        "source_anchor": "south",
        "target_anchor": "north",
        "directionality": "directed",
        "direction": "source_to_target",
        "meaning": "参数更新后执行收敛判定",
        "arrowhead_required": True,
        "arrowhead_present": True,
        "semantics_match": True,
        "source_endpoint_error_pt": 0.0,
        "target_endpoint_error_pt": 0.0,
        "non_target_crossings": 0,
        "min_clearance_pt": 2.5,
        "label_overlap": False,
        "node_interior_overlap": False,
        "final_render_pass": True,
    }
    line = {
        "id": "l01",
        "kind": "flow_arrow",
        "meaning": "从参数更新指向收敛判定",
        "directionality": "directed",
        "expected_direction": "更新节点到判定节点",
        "arrowhead_required": True,
        "arrowhead_present": True,
        "semantics_match": True,
        "final_render_pass": True,
    }
    return {
        "pass": True,
        "checks": checks,
        "style_audit": {
            "family": "tikz",
            "final_min_font_pt": 8.5,
            "line_width_levels": 2,
            "color_count": 2,
            "gradients": False,
            "shadows": False,
            "decorative_icons": False,
            "rounded_card_system": False,
            "math_font_consistent": True,
            "final_vector": True,
            "final_page_checked": True,
            "tikz_stylesheet_used": True,
        },
        "connection_audit": {"total": 1, "checked": 1, "failed": 0, "items": [connection]},
        "line_semantics_audit": {"total": 1, "checked": 1, "failed": 0, "items": [line]},
        "overall_audit": {
            "pass": True,
            "main_axis_clear": True,
            "visual_hierarchy_clear": True,
            "spacing_consistent": True,
            "whitespace_balanced": True,
            "thumbnail_readable": True,
            "full_page_render_checked": True,
        },
    }


def valid_diagram_registry() -> dict:
    return {
        "schema_version": 1,
        "diagrams": [
            {
                "id": "diagram-1",
                "role": "flowchart",
                "purpose": "表达参数更新与判停之间的反馈关系",
                "claim_ids": ["C-Q1-02"],
                "style_family": "tikz",
                "source": "论文/figures/flow.tex",
                "vector_output": "论文/figures/flow.pdf",
                "layout": "论文/figures/flow.layout.json",
                "insert_width_mm": 120,
                "final_min_font_pt": 8.5,
                "generation": {
                    "mode": "mcp",
                    "renderer": "paper-tikz",
                    "tool": "compile_tikz",
                    "health_pass": True,
                    "spec_path": "论文/figures/flow.tex",
                    "provenance_manifest": "审查/provenance/flow.json",
                },
                "vector_audit": {"true_vector": True, "aspect_ratio_distortion": 0.0},
                "visual_review": {
                    "actual_size_render": "审查/renders/flow-actual.png",
                    "full_page_render": "审查/renders/flow-page.png",
                    "thumbnail_render": "审查/renders/flow-thumb.png",
                    "grayscale_render": "审查/renders/flow-gray.png",
                    "publication_ready": True,
                },
            }
        ],
    }


def prepare_figure_case(root: Path, registry: dict) -> None:
    write_placeholder(root / "求解/q1/result.csv", "x,y\n0,0\n")
    write_placeholder(root / "求解/q1/plot.py", "# generated in real project\n")
    write_placeholder(root / "论文/figures/q1.pdf", "%PDF-test\n")
    write_json(root / "审查/provenance/q1.json", {"verified": True})
    for name in ("q1-actual.png", "q1-page.png", "q1-thumb.png", "q1-gray.png"):
        write_placeholder(root / "审查/renders" / name)
    write_json(root / "审查/figure-registry.json", registry)


def prepare_diagram_case(root: Path, registry: dict, layout: dict) -> None:
    write_placeholder(root / "论文/figures/flow.tex", "\\input{cumcm-diagram-styles.tex}\n")
    write_placeholder(root / "论文/figures/flow.pdf", "%PDF-test\n")
    write_json(root / "论文/figures/flow.layout.json", layout)
    write_json(root / "审查/provenance/flow.json", {"verified": True})
    for name in ("flow-actual.png", "flow-page.png", "flow-thumb.png", "flow-gray.png"):
        write_placeholder(root / "审查/renders" / name)
    write_json(root / "审查/diagram-registry.json", registry)


def prepare_chain_case(root: Path) -> None:
    stages = (
        "outline",
        "restatement",
        "analysis",
        "assumptions",
        "notation",
        "model-writing",
        "results-validation",
        "evaluation",
        "references",
        "appendix",
        "abstract",
        "language-audit",
        "figures",
        "diagrams",
    )
    write_placeholder(root / "论文/论文.tex", "% test\n")
    manifest_stages = {}
    for stage in stages:
        gate_rel = f"审查/section-chain/gates/{stage}.json"
        gate = {
            "schema_version": 1,
            "stage": stage,
            "status": "pass",
            "source_files": [] if stage in {"outline", "language-audit"} else ["论文/论文.tex"],
            "checks": [{"id": "selftest", "pass": True, "evidence": "isolated fixture"}],
            "blocking_issues": [],
        }
        write_json(root / gate_rel, gate)
        manifest_stages[stage] = {
            "gate": gate_rel,
            "source_files": gate["source_files"],
        }
    manifest = {
        "schema_version": 1,
        "question_ids": ["q1"],
        "paper_source": "论文/论文.tex",
        "stages": manifest_stages,
        "cross_cutting": {"figures_used": True, "diagrams_used": True},
    }
    write_json(root / "审查/section-chain/manifest.json", manifest)
    write_json(root / "审查/section-chain/language-audit.json", {"pass": True})
    write_json(root / "审查/figure-registry.json", {"schema_version": 1, "figures": [{"id": "f"}]})
    write_json(root / "审查/diagram-registry.json", {"schema_version": 1, "diagrams": [{"id": "d"}]})
    write_json(
        root / "审查/figure-style-audit.json",
        {
            "schema_version": 1,
            "pass": True,
            "registry": "审查/figure-registry.json",
            "figure_count": 1,
        },
    )
    write_json(
        root / "审查/diagram-style-audit.json",
        {
            "schema_version": 1,
            "pass": True,
            "registry": "审查/diagram-registry.json",
            "diagram_count": 1,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="审查/visual-audit-selftest.json")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    skills_root = Path(__file__).resolve().parents[2]
    figure_script = skills_root / "cumcm-figures/scripts/audit_figure_style.py"
    diagram_script = skills_root / "cumcm-diagrams/scripts/audit_diagram_style.py"
    chain_script = skills_root / "cumcm-paper/scripts/audit_section_chain.py"
    cases: dict[str, dict] = {}

    with tempfile.TemporaryDirectory(prefix="cumcm-visual-selftest-") as tmp:
        base = Path(tmp)

        registry = valid_figure_registry()
        root = base / "figure_valid"
        prepare_figure_case(root, registry)
        cases["figure_valid"] = run_case(figure_script, root, True)

        registry = valid_figure_registry()
        registry["figures"][0]["final_min_font_pt"] = 7
        root = base / "figure_low_font"
        prepare_figure_case(root, registry)
        cases["figure_low_font"] = run_case(figure_script, root, False)

        registry = valid_figure_registry()
        registry["figures"][0]["style"]["default_software_theme"] = True
        root = base / "figure_default_theme"
        prepare_figure_case(root, registry)
        cases["figure_default_theme"] = run_case(figure_script, root, False)

        registry = valid_figure_registry()
        registry["figures"][0]["source_data"] = ["求解/q1/missing.csv"]
        root = base / "figure_missing_source"
        prepare_figure_case(root, registry)
        cases["figure_missing_source"] = run_case(figure_script, root, False)

        signature = valid_figure_registry()
        signature["schema_version"] = 3
        signature["visual_identity"] = {
            "identity_id": "cumcm-global-v1",
            "primary_color": "#355C7D",
            "support_color": "#2A9D8F",
            "conclusion_color": "#D98254",
            "semantic_consistency_pass": True,
        }
        signature["signature_policy"] = {
            "track": "national-first",
            "required": True,
            "minimum_count": 1,
            "exemption": None,
        }
        signature_item = signature["figures"][0]
        signature_item.update({
            "signature_figure": True,
            "signature_archetype": "a_mechanism_result",
            "core_claim": "临界状态由约束边界触发并在结果曲线中闭合",
            "ten_second_takeaway": "边界触发后误差降至阈值内",
            "read_order": ["机制与边界", "关键事件", "结论与残差"],
            "data_linkage": {
                "claim_ids": ["C-Q1-01"],
                "source_fields": ["x", "y"],
                "panel_links": ["机制边界->事件点", "事件点->误差闭合"],
                "pass": True,
            },
            "signature_checks": {
                "integrated_narrative": True,
                "mechanism_to_result": True,
                "adds_explanatory_responsibility": True,
                "not_palette_only": True,
                "not_decorative_collage": True,
                "thumbnail_silhouette_pass": True,
                "ten_second_read_pass": True,
                "final_page_visual_pass": True,
            },
        })
        root = base / "signature_valid"
        prepare_figure_case(root, signature)
        cases["signature_valid_national"] = run_case(figure_script, root, True, "--track", "national-first")

        palette_only = deepcopy(signature)
        checks = palette_only["figures"][0]["signature_checks"]
        checks["adds_explanatory_responsibility"] = False
        checks["not_palette_only"] = False
        root = base / "signature_palette_only"
        prepare_figure_case(root, palette_only)
        cases["signature_palette_only_rejected"] = run_case(figure_script, root, False, "--track", "national-first")

        collage = deepcopy(signature)
        collage["figures"][0]["read_order"] = ["左图", "中图", "右图"]
        collage["figures"][0]["data_linkage"]["panel_links"] = []
        collage["figures"][0]["signature_checks"]["integrated_narrative"] = False
        collage["figures"][0]["signature_checks"]["not_decorative_collage"] = False
        root = base / "signature_decorative_collage"
        prepare_figure_case(root, collage)
        cases["signature_decorative_collage_rejected"] = run_case(figure_script, root, False, "--track", "national-first")

        missing_thumbnail = deepcopy(signature)
        missing_thumbnail["figures"][0]["signature_checks"]["thumbnail_silhouette_pass"] = False
        root = base / "signature_missing_thumbnail"
        prepare_figure_case(root, missing_thumbnail)
        cases["signature_thumbnail_rejected"] = run_case(figure_script, root, False, "--track", "national-first")

        exempt = valid_figure_registry()
        exempt["schema_version"] = 3
        exempt["visual_identity"] = signature["visual_identity"]
        exempt["signature_policy"] = {
            "track": "national-first",
            "required": False,
            "minimum_count": 0,
            "exemption": {
                "reason": "题目仅含单变量校准，复合主视觉会重复同一证据",
                "evidence": ["C-Q1-01"],
                "approved_by": "independent-reviewer",
                "review_status": "APPROVED",
            },
        }
        root = base / "signature_justified_exemption"
        prepare_figure_case(root, exempt)
        cases["signature_justified_exemption"] = run_case(figure_script, root, True, "--track", "national-first")

        bad_exempt = deepcopy(exempt)
        bad_exempt["signature_policy"]["exemption"]["reason"] = "不想拼图"
        bad_exempt["signature_policy"]["exemption"]["evidence"] = []
        root = base / "signature_unjustified_exemption"
        prepare_figure_case(root, bad_exempt)
        cases["signature_unjustified_exemption_rejected"] = run_case(figure_script, root, False, "--track", "national-first")

        registry = valid_diagram_registry()
        layout = valid_layout()
        root = base / "diagram_valid"
        prepare_diagram_case(root, registry, layout)
        cases["diagram_valid"] = run_case(diagram_script, root, True)

        registry = valid_diagram_registry()
        registry["diagrams"][0]["final_min_font_pt"] = 7
        root = base / "diagram_low_font"
        prepare_diagram_case(root, registry, valid_layout())
        cases["diagram_low_font"] = run_case(diagram_script, root, False)

        registry = valid_diagram_registry()
        layout = valid_layout()
        layout["connection_audit"]["items"][0]["target_endpoint_error_pt"] = 1.0
        layout["connection_audit"]["items"][0]["non_target_crossings"] = 1
        root = base / "diagram_bad_connection"
        prepare_diagram_case(root, registry, layout)
        cases["diagram_bad_connection"] = run_case(diagram_script, root, False)

        registry = valid_diagram_registry()
        registry["diagrams"][0]["style_family"] = "ppt"
        root = base / "diagram_bad_family"
        prepare_diagram_case(root, registry, valid_layout())
        cases["diagram_bad_family"] = run_case(diagram_script, root, False)

        root = base / "chain_valid"
        prepare_chain_case(root)
        cases["chain_valid"] = run_case(chain_script, root, True)

        root = base / "chain_missing_figure_audit"
        prepare_chain_case(root)
        (root / "审查/figure-style-audit.json").unlink()
        cases["chain_missing_figure_audit"] = run_case(chain_script, root, False)

        root = base / "chain_stale_diagram_audit"
        prepare_chain_case(root)
        report = root / "审查/diagram-style-audit.json"
        registry_path = root / "审查/diagram-registry.json"
        report_time = report.stat().st_mtime
        os.utime(registry_path, (report_time + 5, report_time + 5))
        cases["chain_stale_diagram_audit"] = run_case(chain_script, root, False)

    result = {
        "schema_version": 1,
        "pass": all(item["pass"] for item in cases.values()),
        "case_count": len(cases),
        "cases": cases,
    }
    if not args.no_write:
        output = Path(args.root).resolve() / args.output
        write_json(output, result)
    print(json.dumps({"pass": result["pass"], "case_count": len(cases)}, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
