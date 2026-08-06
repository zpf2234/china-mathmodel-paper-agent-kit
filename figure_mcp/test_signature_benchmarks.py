from __future__ import annotations

import copy
import json
from pathlib import Path

import fitz
import pytest

import signature_benchmarks


SPEC_DIR = Path(__file__).resolve().parent / "benchmarks" / "signature_specs"


def load(name: str) -> dict:
    return json.loads((SPEC_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "name",
    ["a_mechanism_result.json", "b_strategy_landscape.json", "uncertainty_decision_linkage.json"],
)
def test_positive_signature_specs_are_structurally_valid(name: str):
    assert signature_benchmarks.validate_signature_spec(load(name)) == []


def test_palette_only_restyle_is_rejected():
    spec = load("b_strategy_landscape.json")
    spec["signature_checks"]["adds_explanatory_responsibility"] = False
    spec["signature_checks"]["not_palette_only"] = False
    errors = signature_benchmarks.validate_signature_spec(spec)
    assert any("not_palette_only" in error for error in errors)
    assert any("adds_explanatory_responsibility" in error for error in errors)


def test_decorative_collage_without_linkage_is_rejected():
    spec = load("uncertainty_decision_linkage.json")
    spec["read_order"] = ["左图", "中图", "右图"]
    spec["data_linkage"]["element_links"] = []
    spec["signature_checks"]["integrated_narrative"] = False
    spec["signature_checks"]["not_decorative_collage"] = False
    errors = signature_benchmarks.validate_signature_spec(spec)
    assert any("element_links" in error for error in errors)
    assert any("integrated_narrative" in error for error in errors)
    assert any("not_decorative_collage" in error for error in errors)


def test_missing_scientific_evidence_cannot_be_masked_by_complete_style_metadata():
    spec = copy.deepcopy(load("a_mechanism_result.json"))
    del spec["evidence"]["closure_series"]
    errors = signature_benchmarks.validate_signature_spec(spec)
    assert any("evidence missing" in error for error in errors)


def test_a_mechanism_requires_defined_verified_error_and_threshold():
    spec = load("a_mechanism_result.json")
    del spec["evidence"]["closure_series"]["error_definition"]
    del spec["evidence"]["closure_series"]["report_threshold"]
    errors = signature_benchmarks.validate_signature_spec(spec)
    assert any("error_definition" in error for error in errors)
    assert any("report_threshold" in error for error in errors)


def test_strategy_landscape_requires_real_switching_regions():
    spec = load("b_strategy_landscape.json")
    spec["evidence"]["strategy"] = [[1] * len(spec["evidence"]["x"]) for _ in spec["evidence"]["y"]]
    errors = signature_benchmarks.validate_signature_spec(spec)
    assert any("switching boundary" in error for error in errors)


def test_uncertainty_switches_must_bind_threshold_to_sample_size():
    spec = load("uncertainty_decision_linkage.json")
    del spec["evidence"]["switches"][0]["uncertainty_threshold"]
    errors = signature_benchmarks.validate_signature_spec(spec)
    assert any("uncertainty_threshold" in error for error in errors)


def test_generated_scripts_preserve_vector_and_fixed_page_contract():
    pairs = [
        ("a_mechanism_result.json", signature_benchmarks.mechanism_script),
        ("b_strategy_landscape.json", signature_benchmarks.landscape_script),
        ("uncertainty_decision_linkage.json", signature_benchmarks.uncertainty_script),
    ]
    for filename, builder in pairs:
        script = builder(load(filename), "probe")
        assert "PaperSize',[15.500 8.800]" in script
        assert "-dpdf','-painters" in script
        assert "-dsvg" in script
        assert "Resolution',450" in script
        assert "Microsoft YaHei" in script
        assert "'-bestfit'" not in script


def test_render_audit_accepts_real_vector_fixed_size_artifact(tmp_path: Path):
    pdf = tmp_path / "valid.pdf"
    doc = fitz.open()
    page = doc.new_page(width=15.5 / 2.54 * 72, height=8.8 / 2.54 * 72)
    page.insert_text((30, 40), "vector evidence")
    page.draw_line((20, 60), (180, 80))
    doc.save(pdf)
    doc.close()
    svg = tmp_path / "valid.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="15.5cm" height="8.8cm" viewBox="0 0 1550 880"><text x="10" y="20" font-family="Microsoft YaHei">证据</text></svg>', encoding="utf-8")

    audit = signature_benchmarks.audit_rendered_signature(pdf, svg)
    assert audit["pass"] is True
    assert audit["pdf"]["embedded_images"] == 0
    assert audit["pdf"]["page_size_distortion"] <= 0.002
    assert audit["svg"]["aspect_ratio_distortion"] <= 0.002


def test_render_audit_rejects_rasterized_or_deformed_artifact(tmp_path: Path):
    pdf = tmp_path / "bad.pdf"
    doc = fitz.open()
    page = doc.new_page(width=400, height=400)
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 20, 20), False)
    pix.clear_with(200)
    page.insert_image(page.rect, pixmap=pix)
    doc.save(pdf)
    doc.close()
    svg = tmp_path / "bad.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="10cm" height="10cm" viewBox="0 0 100 100"><image href="data:image/png;base64,AA=="/></svg>', encoding="utf-8")

    audit = signature_benchmarks.audit_rendered_signature(pdf, svg)
    assert audit["pass"] is False
    assert any("embedded raster" in error or "distortion" in error for error in audit["errors"])
