from __future__ import annotations

import math
from pathlib import Path

import pytest

import matlab_server
import tikz_server
import visio_server


class _Cell:
    def __init__(self, value: float):
        self.ResultIU = value


class _Shape:
    def __init__(self, x: float, y: float, width: float, height: float, text: str = ""):
        self._cells = {
            "PinX": _Cell(x), "PinY": _Cell(y),
            "Width": _Cell(width), "Height": _Cell(height),
        }
        self.Text = text

    def CellsU(self, name: str):
        return self._cells[name]


class _FormulaCell:
    def __init__(self):
        self.FormulaU = ""


class _TextShape:
    def __init__(self):
        self.Text = ""
        self.cells: dict[str, _FormulaCell] = {}

    def CellsU(self, name: str):
        return self.cells.setdefault(name, _FormulaCell())


def test_decision_default_size_is_not_overwritten_by_process_defaults():
    nodes, _, _ = visio_server.normalize_spec({
        "nodes": [{"id": "d", "type": "decision", "text": "误差小于阈值？"}],
        "edges": [],
    })
    assert nodes[0]["width"] >= 1.75
    assert nodes[0]["height"] >= 0.92


def test_auto_layout_never_shrinks_nodes_below_text_minimum():
    nodes = [
        {"id": f"n{i}", "text": "很长的论文流程节点文字内容", "width": 2.1}
        for i in range(4)
    ]
    spec = {
        "page_width_in": 6.1,
        "nodes": nodes + [{"id": "end", "text": "结束"}],
        "edges": [{"from": f"n{i}", "to": "end"} for i in range(4)],
    }
    resolved, _, meta = visio_server.normalize_spec(spec)
    first_layer = [n for n in resolved if n["id"].startswith("n")]
    assert min(n["width"] for n in first_layer) >= 1.75
    assert meta["page_width_in"] >= 6.1
    for a in first_layer:
        for b in first_layer:
            if a is b:
                continue
            assert abs(a["x"] - b["x"]) >= (a["width"] + b["width"]) / 2


def test_feedback_route_is_orthogonal_and_inside_safe_margin():
    nodes, edges, meta = visio_server.normalize_spec({
        "page_width_in": 6.1,
        "nodes": [
            {"id": "a", "text": "搜索"},
            {"id": "b", "text": "判断", "type": "decision"},
            {"id": "u", "text": "更新"},
        ],
        "edges": [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "u", "label": "否", "branch": "left"},
            {"from": "u", "to": "a", "feedback": True, "dashed": True},
        ],
    })
    feedback = edges[-1]
    assert all(visio_server.STYLE["safe_margin_in"] <= p[0] <= meta["page_width_in"] - visio_server.STYLE["safe_margin_in"] for p in feedback["waypoints"])
    by_id = {n["id"]: _Shape(n["x"], n["y"], n["width"], n["height"]) for n in nodes}
    pts = visio_server.edge_points(by_id["u"], by_id["a"], feedback)
    assert all(math.isclose(a[0], b[0], abs_tol=1e-9) or math.isclose(a[1], b[1], abs_tol=1e-9) for a, b in zip(pts, pts[1:]))


def test_decision_branch_uses_declared_source_port():
    source = _Shape(3.0, 3.0, 2.0, 1.0)
    target = _Shape(1.0, 3.0, 1.5, 0.7)
    pts = visio_server.edge_points(source, target, {"branch": "left", "route": "orthogonal"})
    assert pts[0] == pytest.approx((2.0, 3.0))
    target2 = _Shape(3.0, 1.0, 1.5, 0.7)
    pts2 = visio_server.edge_points(source, target2, {"branch": "bottom", "route": "orthogonal"})
    assert pts2[0] == pytest.approx((3.0, 2.5))


def test_layout_audit_detects_connector_crossing_and_node_overlap():
    shapes = {
        "a": _Shape(1, 3, 1, 0.5, "a"),
        "b": _Shape(5, 3, 1, 0.5, "b"),
        "c": _Shape(3, 5, 1, 0.5, "c"),
        "d": _Shape(3, 1, 1, 0.5, "d"),
        "middle": _Shape(3, 3, 0.8, 0.8, "middle"),
    }
    edges = [{"id": "h", "from": "a", "to": "b", "meaning": "h"}, {"id": "v", "from": "c", "to": "d", "meaning": "v"}]
    paths = [(edges[0], [(1.5, 3), (4.5, 3)]), (edges[1], [(3, 4.75), (3, 1.25)])]
    report = visio_server.build_layout_report({"strict_audit": True}, shapes, edges, paths, 6.1, 6.0)
    assert not report["pass"]
    assert report["checks"]["non_target_crossings_zero"] is False
    assert report["checks"]["connector_crossings_zero"] is False
    assert all(item["connector_crossings"] == 1 for item in report["connection_audit"]["items"])
    assert report["connection_audit"]["failed"] >= 2


def test_valid_mechanical_layout_can_be_publication_ready_before_optional_visual_review():
    shapes = {"a": _Shape(2, 3, 1, 0.5, "a"), "b": _Shape(2, 1, 1, 0.5, "b")}
    edge = {"id": "e", "from": "a", "to": "b", "meaning": "flow"}
    report = visio_server.build_layout_report(
        {"strict_audit": True}, shapes, [edge], [(edge, [(2, 2.75), (2, 1.25)])], 4, 4
    )
    assert report["pass"] is True
    assert report["requires_visual_review"] is True
    assert report["connection_audit"]["failed"] == 0


def test_visio_branch_labels_are_transparent_native_text():
    class _Page:
        def __init__(self):
            self.tag = None
        def DrawRectangle(self, *_args):
            self.tag = _TextShape()
            return self.tag
    page = _Page()
    visio_server.add_label(page, [(0, 0), (2, 0)], "否", {})
    assert page.tag is not None
    assert page.tag.cells["FillPattern"].FormulaU == "0"
    assert page.tag.cells["LinePattern"].FormulaU == "0"


def test_matlab_script_sets_exact_physical_output_size():
    script = matlab_server.build_script({"kind": "line2d", "width_cm": 15.5, "height_cm": 8.8, "series": [{"x": [0, 1], "y": [0, 1]}]}, Path("."), "x")
    assert "PaperSize',[15.500 8.800]" in script
    assert "-dpdf" in script and "-painters" in script


def test_tikz_document_honors_requested_width_without_scaling_fonts():
    tex = tikz_server.document(r"\draw (0,0)--(2,0);", width_cm=15.5, border_pt=0)
    assert r"rectangle (15.5cm,0 |- paper-bbox-north)" in tex
    assert r"\pgfresetboundingbox" in tex
    assert tex.index(r"\draw (0,0)--(2,0);") < tex.index(r"use as bounding box")
    assert r"\resizebox" not in tex


def test_compile_tikz_preserves_complete_picture_options_and_injects_fixed_width_box():
    picture = r"""\begin{tikzpicture}[x=2cm,y=3cm,scale=.75]
\draw (0,0)--(2,1);
\end{tikzpicture}"""
    tex = tikz_server.document(picture, width_cm=12.3, border_pt=0)
    assert r"\begin{tikzpicture}[x=2cm,y=3cm,scale=.75]" in tex
    assert tex.count(r"\begin{tikzpicture}") == 1
    assert r"rectangle (12.3cm,0 |- paper-bbox-north)" in tex


def test_compile_tikz_trusts_explicit_canvas_without_second_bbox_reset():
    picture = r"""\begin{tikzpicture}
\path[use as bounding box] (0,0) rectangle (15.5,8.8);
\draw (0,0)--(2,1);
\end{tikzpicture}"""
    tex = tikz_server.document(picture, width_cm=15.5, border_pt=0)
    assert tex.count("use as bounding box") == 1
    assert r"\pgfresetboundingbox" not in tex


def test_tikz_formula_and_dimension_labels_are_transparent_by_default():
    body = tikz_server.build_from_spec({"elements": [
        {"type": "line", "from": [0, 0], "to": [2, 0], "label": "$g_{ij}>0$"},
        {"type": "dimension", "from": [0, -1], "to": [2, -1], "label": "$L$"},
    ]})
    assert "fill=white" not in body
    assert "$g_{ij}>0$" in body and "$L$" in body


def test_structured_tikz_canvas_is_not_collapsed_by_second_bbox_reset():
    body = tikz_server.build_from_spec({"canvas": {"width": 15.5, "height": 7.2}, "elements": [
        {"type": "line", "from": [0, 0], "to": [2, 1]},
    ]})
    tex = tikz_server.document(body, width_cm=15.5, border_pt=0)
    assert tex.count("use as bounding box") == 1
    assert r"\pgfresetboundingbox" not in tex


def test_tikz_detail_inset_is_native_geometry_not_raster():
    body = tikz_server.build_from_spec({"elements": [{
        "type": "detail_inset", "source_center": [1, 1], "inset_center": [6, 3],
        "elements": [{"type": "line", "from": [-1, 0], "to": [1, 0]}],
    }]})
    assert "includegraphics" not in body
    assert "densely dashed" in body and "begin{scope}" in body


def test_editorial_spine_preset_adds_hierarchy_without_gradients_or_shadows():
    nodes, edges, _ = visio_server.normalize_spec({
        "visual_preset": "editorial-spine", "focus_node": "b",
        "nodes": [{"id": "a", "text": "输入"}, {"id": "b", "text": "核心"}, {"id": "d", "type": "decision", "text": "通过？"}],
        "edges": [{"from": "a", "to": "b"}, {"kind": "decision_branch", "from": "d", "to": "a", "label": "否"}],
    })
    by_id = {node["id"]: node for node in nodes}
    assert by_id["b"]["bold"] is True and by_id["b"]["line_weight_pt"] > by_id["a"]["line_weight_pt"]
    assert by_id["d"]["line"] == "#B44C43"
    assert edges[1]["line"] == "#B44C43"
    assert by_id["a"]["width"] <= 1.72 and by_id["d"]["height"] == pytest.approx(0.80)


def test_visio_sets_latin_and_east_asian_character_fonts_to_yahei():
    shape = _TextShape()
    visio_server.shape_text(shape, "中文 ABC")
    assert shape.cells["Char.Font"].FormulaU == 'FONT("微软雅黑")'
    assert shape.cells["Char.AsianFont"].FormulaU == 'FONT("微软雅黑")'


def test_matlab_pdf_export_does_not_allow_bestfit_to_override_paper_size():
    script = matlab_server.build_script(
        {"kind": "line2d", "width_cm": 15.5, "height_cm": 8.8, "series": [{"x": [0, 1], "y": [0, 1]}]},
        Path("."),
        "x",
    )
    assert "'-bestfit'" not in script
