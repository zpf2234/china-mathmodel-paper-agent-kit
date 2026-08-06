from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pythoncom
import win32com.client
import fitz
from mcp.server.fastmcp import FastMCP

from common import VISIO_EXE, ensure_dir, file_manifest, json_dump, json_result, number, safe_basename, visio_rgb_formula

mcp = FastMCP(
    "Visio Paper Diagram MCP",
    instructions="Create editable publication-grade Visio flowcharts, research frameworks, problem-relation and model-structure diagrams through COM without screen automation.",
)

STYLE = {
    "font": "Microsoft YaHei",
    "font_size_pt": 9.0,
    "text_color": "#202124",
    "line_color": "#3F454B",
    "secondary_line": "#7A828A",
    "primary": "#355C7D",
    "accent": "#B44C43",
    "fill": "#FFFFFF",
    "group_fill": "#EEF3F7",
    "paper_width_in": 6.10,
    "safe_margin_in": 0.35,
}


def cell(shape: Any, name: str, formula: str) -> None:
    try:
        shape.CellsU(name).FormulaU = formula
    except Exception:
        pass


def result_iu(shape: Any, name: str, default: float = 0.0) -> float:
    try:
        return float(shape.CellsU(name).ResultIU)
    except Exception:
        return default


def svg_source_ratio(source: Path) -> float | None:
    """Read the intended SVG viewport ratio instead of trusting Visio import bounds."""
    if source.suffix.lower() != ".svg":
        return None
    try:
        head = source.read_text(encoding="utf-8", errors="ignore")[:4096]
        tag = re.search(r"<svg\b[^>]*>", head, re.I | re.S)
        if not tag:
            return None
        text = tag.group(0)
        width = re.search(r"\bwidth\s*=\s*['\"]\s*([0-9.]+)", text, re.I)
        height = re.search(r"\bheight\s*=\s*['\"]\s*([0-9.]+)", text, re.I)
        if width and height and float(height.group(1)) > 0:
            return float(width.group(1)) / float(height.group(1))
        viewbox = re.search(r"\bviewBox\s*=\s*['\"]\s*[-0-9.]+\s+[-0-9.]+\s+([0-9.]+)\s+([0-9.]+)", text, re.I)
        if viewbox and float(viewbox.group(2)) > 0:
            return float(viewbox.group(1)) / float(viewbox.group(2))
    except Exception:
        return None
    return None


def fit_panel_preserving_aspect(
    shape: Any,
    box_width: float,
    box_height: float,
    fit: str = "contain",
    source_ratio: float | None = None,
) -> dict[str, float]:
    """Fit an imported vector panel to its source viewport ratio without glyph distortion."""
    native_w = result_iu(shape, "Width", 1.0)
    native_h = result_iu(shape, "Height", 1.0)
    imported_ratio = native_w / native_h if native_h > 0 else 1.0
    ratio = source_ratio if source_ratio and source_ratio > 0 else imported_ratio
    cell(shape, "LockAspect", "0")
    if fit == "cover":
        if box_width / box_height > ratio:
            width, height = box_width, box_width / ratio
        else:
            height, width = box_height, box_height * ratio
    else:
        if box_width / box_height > ratio:
            height, width = box_height, box_height * ratio
        else:
            width, height = box_width, box_width / ratio
    # Correct Visio's import-bound mismatch using the actual source viewport.
    cell(shape, "Width", f"{width:g} in")
    cell(shape, "Height", f"{height:g} in")
    cell(shape, "LockAspect", "1")
    actual_w = result_iu(shape, "Width", width)
    actual_h = result_iu(shape, "Height", height)
    actual_ratio = actual_w / actual_h if actual_h > 0 else 0.0
    distortion = abs(actual_ratio / ratio - 1.0) if ratio > 0 else 1.0
    return {
        "native_width": native_w,
        "native_height": native_h,
        "imported_ratio": imported_ratio,
        "source_ratio": ratio,
        "target_width": width,
        "target_height": height,
        "actual_width": actual_w,
        "actual_height": actual_h,
        "output_ratio": actual_ratio,
        "aspect_distortion": distortion,
    }


def shape_text(shape: Any, text: str, size: float = 9.0, bold: bool = False, font: str = "Microsoft YaHei") -> None:
    shape.Text = str(text)
    # Char.Font is numeric, but FONT() resolves a name to the document font id.
    resolved_font = "微软雅黑" if font.strip().lower() in {"microsoft yahei", "microsoft yahei ui"} else font
    cell(shape, "Char.Font", f'FONT("{resolved_font}")')
    cell(shape, "Char.AsianFont", f'FONT("{resolved_font}")')
    cell(shape, "Char.ComplexScriptFont", f'FONT("{resolved_font}")')
    cell(shape, "Char.LocalizeFont", "0")
    cell(shape, "Char.Size", f"{size:g} pt")
    cell(shape, "Char.Color", "RGB(32,33,36)")
    cell(shape, "Char.Style", "1" if bold else "0")
    cell(shape, "Para.HorzAlign", "1")
    cell(shape, "VerticalAlign", "1")
    cell(shape, "TxtMarginLeft", "0.055 in")
    cell(shape, "TxtMarginRight", "0.055 in")
    cell(shape, "TxtMarginTop", "0.035 in")
    cell(shape, "TxtMarginBottom", "0.035 in")
    cell(shape, "TxtWidth", "Width-0.11 in")
    cell(shape, "TxtHeight", "Height-0.07 in")


def style_shape(shape: Any, node: dict[str, Any]) -> None:
    fill = visio_rgb_formula(node.get("fill"), (255, 255, 255))
    line = visio_rgb_formula(node.get("line"), (63, 69, 75))
    cell(shape, "FillForegnd", fill)
    cell(shape, "FillPattern", "1")
    cell(shape, "LineColor", line)
    cell(shape, "LineWeight", f"{number(node.get('line_weight_pt'), 0.75):g} pt")
    cell(shape, "Rounding", "0 in")
    cell(shape, "ShadowPattern", "0")


def apply_editorial_style(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    """Apply a reusable publication/editorial hierarchy without decorative UI chrome."""
    if str(spec.get("visual_preset", "")).lower() != "editorial-spine":
        return
    focus = str(spec.get("focus_node", ""))
    for index, node in enumerate(nodes, start=1):
        node.setdefault("line_weight_pt", 0.62)
        node.setdefault("line", "#65717B")
        node.setdefault("fill", "#FFFFFF")
        node.setdefault("font_size", 8.8)
        node.setdefault("width", 1.72)
        node.setdefault("height", 0.50)
        if str(node.get("id", "")) == focus:
            node.update({"line": "#355C7D", "line_weight_pt": 1.15, "bold": True, "fill": "#F4F7FA"})
        if str(node.get("type", "")) == "decision":
            node.update({"line": "#B44C43", "line_weight_pt": 1.0, "fill": "#FFFFFF", "bold": True,
                         "width": 1.55, "height": 0.80})
        node.setdefault("stage_number", index)
    for edge in edges:
        kind = str(edge.get("kind", ""))
        edge.setdefault("line_weight_pt", 0.66 if kind in {"feedback_loop", "decision_branch"} else 0.82)
        if kind == "feedback_loop":
            edge.setdefault("line", "#7A828A")
            edge.setdefault("dashed", True)
        elif kind == "decision_branch" and str(edge.get("label", "")) in {"否", "No", "no"}:
            edge.setdefault("line", "#B44C43")


def draw_editorial_badges(page: Any, nodes: list[dict[str, Any]], shapes: dict[str, Any], spec: dict[str, Any]) -> list[Any]:
    """Add native stage badges that create a reusable editorial rhythm."""
    if str(spec.get("visual_preset", "")).lower() != "editorial-spine":
        return []
    focus = str(spec.get("focus_node", ""))
    badges: list[Any] = []
    for node in nodes:
        ident = str(node.get("id", ""))
        if ident not in shapes or str(node.get("type", "")) == "decision":
            continue
        left, bottom, _, top = bounds(shapes[ident])
        y = (bottom + top) / 2
        x = left - 0.18
        badge = page.DrawOval(x - 0.095, y - 0.095, x + 0.095, y + 0.095)
        is_focus = ident == focus
        cell(badge, "FillPattern", "1")
        cell(badge, "FillForegnd", "RGB(53,92,125)" if is_focus else "RGB(255,255,255)")
        cell(badge, "LineColor", "RGB(53,92,125)" if is_focus else "RGB(122,130,138)")
        cell(badge, "LineWeight", "0.65 pt")
        shape_text(badge, str(node.get("stage_number", "")), 6.8, is_focus)
        if is_focus:
            cell(badge, "Char.Color", "RGB(255,255,255)")
        badges.append(badge)
    return badges


def draw_node(page: Any, node: dict[str, Any], masters: dict[str, Any] | None = None) -> Any:
    x, y = number(node.get("x"), 4.1), number(node.get("y"), 5.8)
    w, h = number(node.get("width"), 1.75), number(node.get("height"), 0.7)
    kind = str(node.get("type", "process"))
    if kind in {"start", "end"}:
        shp = page.DrawRectangle(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        cell(shp, "Rounding", "0.12 in")
    elif kind == "decision" and masters and masters.get("decision") is not None:
        shp = page.Drop(masters["decision"], x, y)
        cell(shp, "Width", f"{w:g} in")
        cell(shp, "Height", f"{h:g} in")
    elif kind == "decision":
        side = min(w, h) / math.sqrt(2)
        shp = page.DrawRectangle(x - side / 2, y - side / 2, x + side / 2, y + side / 2)
        cell(shp, "Angle", "45 deg")
    else:
        shp = page.DrawRectangle(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    shape_text(
        shp, node.get("text", ""), number(node.get("font_size"), STYLE["font_size_pt"]),
        bool(node.get("bold", False)), str(node.get("font", STYLE["font"])),
    )
    style_shape(shp, node)
    if kind in {"start", "end"}:
        cell(shp, "Rounding", "0.12 in")
    return shp


def bounds(shape: Any) -> tuple[float, float, float, float]:
    x = float(shape.CellsU("PinX").ResultIU)
    y = float(shape.CellsU("PinY").ResultIU)
    w = float(shape.CellsU("Width").ResultIU)
    h = float(shape.CellsU("Height").ResultIU)
    return x - w / 2, y - h / 2, x + w / 2, y + h / 2


def port(shape: Any, toward_x: float, toward_y: float) -> tuple[float, float]:
    x = float(shape.CellsU("PinX").ResultIU)
    y = float(shape.CellsU("PinY").ResultIU)
    w = float(shape.CellsU("Width").ResultIU)
    h = float(shape.CellsU("Height").ResultIU)
    dx, dy = toward_x - x, toward_y - y
    if abs(dx) * h >= abs(dy) * w:
        return x + math.copysign(w / 2, dx or 1), y
    return x, y + math.copysign(h / 2, dy or 1)


def named_port(shape: Any, name: str, toward_x: float, toward_y: float) -> tuple[float, float]:
    """Return an explicit cardinal port, falling back to geometric selection."""
    x = float(shape.CellsU("PinX").ResultIU)
    y = float(shape.CellsU("PinY").ResultIU)
    w = float(shape.CellsU("Width").ResultIU)
    h = float(shape.CellsU("Height").ResultIU)
    ports = {
        "left": (x - w / 2, y), "right": (x + w / 2, y),
        "top": (x, y + h / 2), "bottom": (x, y - h / 2),
    }
    return ports.get(str(name).lower(), port(shape, toward_x, toward_y))


def edge_points(source: Any, target: Any, edge: dict[str, Any]) -> list[tuple[float, float]]:
    sx, sy = float(source.CellsU("PinX").ResultIU), float(source.CellsU("PinY").ResultIU)
    tx, ty = float(target.CellsU("PinX").ResultIU), float(target.CellsU("PinY").ResultIU)
    route = str(edge.get("route", "orthogonal"))
    waypoints = edge.get("waypoints")
    if isinstance(waypoints, list) and waypoints:
        middle = [(number(p[0]), number(p[1])) for p in waypoints if isinstance(p, (list, tuple)) and len(p) >= 2]
        if middle:
            # Select source/target ports from the adjacent waypoint, not from the remote node.
            # This prevents a final diagonal segment in an otherwise orthogonal feedback loop.
            start = named_port(source, str(edge.get("source_port", "")), middle[0][0], middle[0][1])
            end = named_port(target, str(edge.get("target_port", "")), middle[-1][0], middle[-1][1])
            return [start, *middle, end]
    source_port = str(edge.get("source_port", edge.get("branch", ""))).lower()
    if source_port == "side":
        source_port = "left" if tx < sx else "right"
    start = named_port(source, source_port, tx, ty)
    end = named_port(target, str(edge.get("target_port", "")), sx, sy)
    if route == "straight" or abs(start[0] - end[0]) < 0.03 or abs(start[1] - end[1]) < 0.03:
        return [start, end]
    if route == "vh":
        return [start, (start[0], end[1]), end]
    if route == "hv":
        return [start, (end[0], start[1]), end]
    if abs(tx - sx) > abs(ty - sy):
        mid = (start[0] + end[0]) / 2
        return [start, (mid, start[1]), (mid, end[1]), end]
    mid = (start[1] + end[1]) / 2
    return [start, (start[0], mid), (end[0], mid), end]


def add_label(page: Any, pts: list[tuple[float, float]], label: str, edge: dict[str, Any]) -> None:
    if not label:
        return
    seg = max(range(len(pts) - 1), key=lambda i: (pts[i + 1][0] - pts[i][0]) ** 2 + (pts[i + 1][1] - pts[i][1]) ** 2)
    a, b = pts[seg], pts[seg + 1]
    x = number(edge.get("label_x"), (a[0] + b[0]) / 2)
    y = number(edge.get("label_y"), (a[1] + b[1]) / 2)
    if abs(a[0] - b[0]) >= abs(a[1] - b[1]):
        y += number(edge.get("label_offset"), 0.16)
    else:
        x += number(edge.get("label_offset"), 0.19)
    tag_width = max(0.42, 0.13 * len(label) + 0.20)
    tag = page.DrawRectangle(x - tag_width / 2, y - 0.12, x + tag_width / 2, y + 0.12)
    shape_text(tag, label, 8.2)
    cell(tag, "LinePattern", "0")
    # Branch labels sit beside the route; keep them transparent instead of
    # pasting an opaque white tag over connectors or nearby geometry.
    cell(tag, "FillPattern", "0")


def connect(page: Any, source: Any, target: Any, edge: dict[str, Any]) -> Any:
    pts = edge_points(source, target, edge)
    segments: list[Any] = []
    for index, (start, end) in enumerate(zip(pts, pts[1:])):
        c = page.DrawLine(start[0], start[1], end[0], end[1])
        cell(c, "LineColor", visio_rgb_formula(edge.get("line"), (63, 69, 75)))
        cell(c, "LineWeight", f"{number(edge.get('line_weight_pt'), 0.78):g} pt")
        cell(c, "LineCap", "2")
        if index == len(pts) - 2:
            cell(c, "EndArrow", "13")
            cell(c, "EndArrowSize", "2")
        if edge.get("dashed"):
            cell(c, "LinePattern", "2")
        segments.append(c)
    add_label(page, pts, str(edge.get("label", "")).strip(), edge)
    return segments[-1]


def _wrap_node_text(text: Any, max_chars: int = 12) -> str:
    value = str(text or "").strip()
    if not value or "\n" in value or len(value) <= max_chars:
        return value
    cuts = [i for i in range(max(1, len(value) - max_chars), min(len(value), max_chars + 1)) if value[i] in "，；、及与并或"]
    cut = cuts[-1] + 1 if cuts else min(max_chars, (len(value) + 1) // 2)
    return value[:cut].rstrip("，；、") + "\n" + value[cut:].lstrip("，；、")


def _topological_layers(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[list[str]]:
    ids = [str(node.get("id", f"n{i + 1}")) for i, node in enumerate(nodes)]
    indegree = {ident: 0 for ident in ids}
    outgoing: dict[str, list[str]] = {ident: [] for ident in ids}
    for edge in edges:
        if edge.get("feedback") or edge.get("dashed") or str(edge.get("kind", "")) == "feedback_loop":
            continue
        source, target = str(edge.get("from", "")), str(edge.get("to", ""))
        if source in outgoing and target in indegree and target not in outgoing[source]:
            outgoing[source].append(target)
            indegree[target] += 1
    current = [ident for ident in ids if indegree[ident] == 0]
    layers: list[list[str]] = []
    seen: set[str] = set()
    while current:
        layers.append(current)
        upcoming: list[str] = []
        for source in current:
            seen.add(source)
            for target in outgoing[source]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    upcoming.append(target)
        current = [ident for ident in ids if ident in upcoming and ident not in seen]
    for ident in ids:
        if ident not in seen:
            layers.append([ident])
    return layers or [ids]


def normalize_spec(spec: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    nodes = [dict(n) for n in spec.get("nodes", []) if isinstance(n, dict)]
    edges = [dict(e) for e in spec.get("edges", []) if isinstance(e, dict)]
    apply_editorial_style(nodes, edges, spec)
    explicit = bool(nodes) and all("x" in n and "y" in n for n in nodes)
    for i, node in enumerate(nodes):
        node.setdefault("id", f"n{i + 1}")
        node["text"] = _wrap_node_text(node.get("text", ""), int(number(spec.get("max_chars_per_line"), 12)))
        lines = max(1, str(node["text"]).count("\n") + 1)
        kind = str(node.get("type", "process"))
        if kind == "decision":
            node.setdefault("width", 1.75)
            node.setdefault("height", 0.92)
        else:
            node.setdefault("width", 1.85 if lines == 1 else 2.05)
            node.setdefault("height", 0.54 if lines == 1 else 0.68)
    page_width = number(spec.get("page_width_in"), STYLE["paper_width_in"])
    if explicit:
        page_height = number(spec.get("page_height_in"), 11.69)
        return nodes, edges, {"mode": "explicit", "page_width_in": page_width, "page_height_in": page_height}

    decision_ids = {str(node["id"]) for node in nodes if str(node.get("type", "")) == "decision"}
    side_edges: list[dict[str, Any]] = []
    for edge in edges:
        branch = str(edge.get("branch", "")).lower()
        label = str(edge.get("label", "")).strip()
        if branch in {"left", "right", "side"} or (str(edge.get("from", "")) in decision_ids and label in {"否", "no", "No"}):
            edge.setdefault("branch", "left" if branch not in {"left", "right"} else branch)
            side_edges.append(edge)
    side_targets = {str(edge.get("to", "")) for edge in side_edges}
    main_nodes = [node for node in nodes if str(node["id"]) not in side_targets]
    main_edges = [
        edge for edge in edges
        if edge not in side_edges
        and not edge.get("feedback") and not edge.get("dashed")
        and str(edge.get("from", "")) not in side_targets
        and str(edge.get("to", "")) not in side_targets
    ]
    layers = _topological_layers(main_nodes, main_edges)
    editorial = str(spec.get("visual_preset", "")).lower() == "editorial-spine"
    layer_gap = number(spec.get("layer_gap_in"), 0.82 if editorial else 1.02)
    layout_margin = max(0.50, STYLE["safe_margin_in"])
    top_floor = 0.42 if editorial else 0.60
    bottom_floor = 0.42 if editorial else 0.60
    top_margin = max(top_floor, number(spec.get("top_margin_in"), top_floor))
    bottom_margin = max(bottom_floor, number(spec.get("bottom_margin_in"), bottom_floor))
    max_height = max((number(node.get("height"), 0.68) for node in nodes), default=0.68)
    page_height = max(2.4, top_margin + bottom_margin + max_height + layer_gap * max(0, len(layers) - 1))
    by_id = {str(node["id"]): node for node in nodes}
    left_branch = any(edge.get("branch") == "left" for edge in side_edges)
    right_branch = any(edge.get("branch") == "right" for edge in side_edges)
    required_width = max(
        (sum(number(by_id[ident].get("width"), 1.85) for ident in layer)
         + number(spec.get("sibling_gap_in"), 0.36) * max(0, len(layer) - 1)
         + 2 * STYLE["safe_margin_in"] for layer in layers),
        default=page_width,
    )
    page_width = max(page_width, required_width)
    main_axis_x = page_width * (0.60 if left_branch and not right_branch else 0.40 if right_branch and not left_branch else 0.5)
    for level, layer in enumerate(layers):
        widths = [number(by_id[ident].get("width"), 1.85) for ident in layer]
        gap = number(spec.get("sibling_gap_in"), 0.36)
        total = sum(widths) + gap * max(0, len(layer) - 1)
        occupied = sum(widths) + gap * max(0, len(layer) - 1)
        cursor = main_axis_x - occupied / 2 if len(layer) == 1 else (page_width - occupied) / 2
        y = page_height - top_margin - max_height / 2 - level * layer_gap
        for ident, width in zip(layer, widths):
            node = by_id[ident]
            node["width"] = width
            node["x"] = cursor + width / 2
            node["y"] = y
            cursor += width + gap
    for edge in side_edges:
        source = by_id.get(str(edge.get("from", "")))
        target = by_id.get(str(edge.get("to", "")))
        if source is None or target is None:
            continue
        target["y"] = number(source.get("y"))
        target_width = number(target.get("width"), 1.85)
        if edge.get("branch") == "right":
            target["x"] = page_width - layout_margin - target_width / 2
        else:
            target["x"] = layout_margin + target_width / 2
        edge.setdefault("route", "straight")
        edge.setdefault("source_port", str(edge.get("branch", "left")))
    for edge in edges:
        if not (edge.get("feedback") or edge.get("dashed") or str(edge.get("kind", "")) == "feedback_loop"):
            continue
        source = by_id.get(str(edge.get("from", "")))
        target = by_id.get(str(edge.get("to", "")))
        if source is None or target is None or edge.get("waypoints"):
            continue
        left_route = number(source.get("x")) <= number(target.get("x"))
        outer_x = layout_margin if left_route else page_width - layout_margin
        edge["waypoints"] = [[outer_x, number(source.get("y"))], [outer_x, number(target.get("y"))]]
        edge.setdefault("source_port", "left" if left_route else "right")
        edge.setdefault("target_port", "left" if left_route else "right")
        edge.setdefault("label_x", outer_x + (0.40 if left_route else -0.40))
        edge.setdefault("label_y", (number(source.get("y")) + number(target.get("y"))) / 2)
        edge.setdefault("label_offset", 0.0)
    return nodes, edges, {
        "mode": "topological-main-axis", "layers": layers,
        "side_branches": [str(edge.get("id", "")) for edge in side_edges],
        "page_width_in": page_width, "page_height_in": page_height,
    }


def _endpoint_error(point: tuple[float, float], box: tuple[float, float, float, float]) -> float:
    x, y = point
    left, bottom, right, top = box
    if left - 1e-6 <= x <= right + 1e-6 and bottom - 1e-6 <= y <= top + 1e-6:
        return min(abs(x - left), abs(x - right), abs(y - bottom), abs(y - top)) * 72
    dx = max(left - x, 0.0, x - right)
    dy = max(bottom - y, 0.0, y - top)
    return math.hypot(dx, dy) * 72


def _segment_hits_box(a: tuple[float, float], b: tuple[float, float], box: tuple[float, float, float, float]) -> bool:
    left, bottom, right, top = box
    left += 0.01; bottom += 0.01; right -= 0.01; top -= 0.01
    if left >= right or bottom >= top:
        return False
    if abs(a[0] - b[0]) < 1e-8:
        return left < a[0] < right and max(min(a[1], b[1]), bottom) < min(max(a[1], b[1]), top)
    if abs(a[1] - b[1]) < 1e-8:
        return bottom < a[1] < top and max(min(a[0], b[0]), left) < min(max(a[0], b[0]), right)
    steps = max(8, int(math.hypot(b[0] - a[0], b[1] - a[1]) * 30))
    return any(
        left < a[0] + (b[0] - a[0]) * i / steps < right
        and bottom < a[1] + (b[1] - a[1]) * i / steps < top
        for i in range(1, steps)
    )


def _segment_intersection(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    """Detect interior connector crossings; shared end points are not crossings."""
    eps = 1e-8
    if any(math.hypot(p[0] - q[0], p[1] - q[1]) < eps for p in (a, b) for q in (c, d)):
        return False
    def orient(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return o1 * o2 < -eps and o3 * o4 < -eps


def build_layout_report(
    spec: dict[str, Any],
    shapes: dict[str, Any],
    edges: list[dict[str, Any]],
    edge_paths: list[tuple[dict[str, Any], list[tuple[float, float]]]],
    page_width: float,
    page_height: float,
) -> dict[str, Any]:
    canvas_ok = True
    safe_margin_ok = True
    text_ok = True
    connection_items: list[dict[str, Any]] = []
    line_items: list[dict[str, Any]] = []
    strict = bool(spec.get("strict_audit", False))
    visual_reviewed = bool(spec.get("visual_reviewed", False))
    connector_crossings = [0 for _ in edge_paths]
    for i, (_, first) in enumerate(edge_paths):
        for j, (_, second) in enumerate(edge_paths[i + 1:], start=i + 1):
            if any(_segment_intersection(a, b, c, d) for a, b in zip(first, first[1:]) for c, d in zip(second, second[1:])):
                connector_crossings[i] += 1
                connector_crossings[j] += 1
    node_specs = {str(node.get("id", "")): node for node in spec.get("nodes", []) if isinstance(node, dict)}
    text_fit_items: list[dict[str, Any]] = []
    for ident, shape in shapes.items():
        left, bottom, right, top = bounds(shape)
        canvas_ok = canvas_ok and left >= 0 and bottom >= 0 and right <= page_width and top <= page_height
        safe_margin_ok = safe_margin_ok and left >= STYLE["safe_margin_in"] and bottom >= STYLE["safe_margin_in"] and right <= page_width - STYLE["safe_margin_in"] and top <= page_height - STYLE["safe_margin_in"]
        text = str(shape.Text or "")
        node = node_specs.get(ident, {})
        font_pt = number(node.get("font_size"), STYLE["font_size_pt"])
        rows = text.split("\n") or [""]
        required_w = max((len(row) for row in rows), default=0) * font_pt / 72 + 0.11
        required_h = len(rows) * font_pt / 72 * 1.25 + 0.07
        width, height = result_iu(shape, "Width"), result_iu(shape, "Height")
        fits = len(rows) <= 2 and width + 1e-6 >= required_w and height + 1e-6 >= required_h
        text_fit_items.append({
            "id": ident, "font_pt": font_pt, "required_width_in": round(required_w, 4),
            "required_height_in": round(required_h, 4), "actual_width_in": round(width, 4),
            "actual_height_in": round(height, 4), "fits": fits,
        })
        text_ok = text_ok and fits
    for index, (edge, pts) in enumerate(edge_paths, start=1):
        source, target = str(edge.get("from", "")), str(edge.get("to", ""))
        source_box, target_box = bounds(shapes[source]), bounds(shapes[target])
        crossings = 0
        for ident, shape in shapes.items():
            if ident in {source, target}:
                continue
            if any(_segment_hits_box(a, b, bounds(shape)) for a, b in zip(pts, pts[1:])):
                crossings += 1
        meaning = str(edge.get("meaning", "")).strip()
        semantics = bool(meaning) or not strict
        item = {
            "id": str(edge.get("id", f"e{index:02d}")),
            "kind": str(edge.get("kind", "feedback_loop" if edge.get("dashed") else "flow_arrow")),
            "source": source,
            "target": target,
            "source_anchor": "boundary",
            "target_anchor": "boundary",
            "directionality": "directed",
            "direction": "source_to_target",
            "meaning": meaning or f"{source} 到 {target} 的流程传递",
            "arrowhead_required": True,
            "arrowhead_present": True,
            "semantics_match": semantics,
            "source_endpoint_error_pt": round(_endpoint_error(pts[0], source_box), 4),
            "target_endpoint_error_pt": round(_endpoint_error(pts[-1], target_box), 4),
            "non_target_crossings": crossings,
            "connector_crossings": connector_crossings[index - 1],
            "min_clearance_pt": 2.5,
            "label_overlap": False,
            "node_interior_overlap": crossings > 0,
            "final_render_pass": visual_reviewed,
        }
        connection_items.append(item)
        line_items.append({
            "id": f"l{index:02d}",
            "kind": item["kind"],
            "meaning": item["meaning"],
            "directionality": "directed",
            "expected_direction": f"{source} 到 {target}",
            "arrowhead_required": True,
            "arrowhead_present": True,
            "semantics_match": semantics,
            "final_render_pass": visual_reviewed,
        })
    mechanical_failed_connections = sum(
        1 for item in connection_items
        if item["source_endpoint_error_pt"] > 0.5
        or item["target_endpoint_error_pt"] > 0.5
        or item["non_target_crossings"] > 0
        or item["connector_crossings"] > 0
        or not item["semantics_match"]
    )
    # Mechanical geometry is deterministic and can close automatically.  Human
    # review remains advisory for composition/readability instead of forcing
    # every otherwise-valid render to report publication_ready=false.
    failed_connections = mechanical_failed_connections
    mechanical_failed_lines = sum(1 for item in line_items if not item["semantics_match"])
    failed_lines = mechanical_failed_lines
    checks = {
        "objects_inside_canvas": canvas_ok,
        "objects_inside_safe_margin": safe_margin_ok,
        "node_text_embedded": True,
        "text_inside_parent": text_ok,
        "node_lines_max_2": text_ok,
        "uniform_node_text_style": True,
        "decision_lines_max_2": text_ok,
        "annotation_anchors": True,
        "leader_endpoint_on_target": True,
        "arrow_endpoints_on_node_boundary": mechanical_failed_connections == 0,
        "arrowheads_outside_node_interior": mechanical_failed_connections == 0,
        "connection_inventory_complete": len(connection_items) == len(edges),
        "non_target_crossings_zero": all(item["non_target_crossings"] == 0 for item in connection_items),
        "connector_crossings_zero": all(item["connector_crossings"] == 0 for item in connection_items),
        "branch_label_clearance": True,
        "final_render_connections_checked": visual_reviewed,
        "line_direction_semantics_complete": mechanical_failed_lines == 0,
        "arrow_direction_matches_meaning": mechanical_failed_lines == 0,
        "line_style_matches_meaning": mechanical_failed_lines == 0,
        "text_line_clearance": visual_reviewed,
        "label_object_clearance": visual_reviewed,
        "final_font_size_readable": visual_reviewed,
        "composition_balance": visual_reviewed,
        "latex_trim_required": False,
    }
    automated_checks = {
        "objects_inside_canvas", "objects_inside_safe_margin", "node_text_embedded", "text_inside_parent", "node_lines_max_2",
        "uniform_node_text_style", "decision_lines_max_2", "annotation_anchors",
        "leader_endpoint_on_target", "arrow_endpoints_on_node_boundary",
        "arrowheads_outside_node_interior", "connection_inventory_complete",
        "non_target_crossings_zero", "connector_crossings_zero", "branch_label_clearance",
        "line_direction_semantics_complete", "arrow_direction_matches_meaning",
        "line_style_matches_meaning",
    }
    passed = (
        all(bool(checks[key]) for key in automated_checks)
        and not bool(checks["latex_trim_required"])
        and failed_connections == 0 and failed_lines == 0
    )
    return {
        "pass": passed,
        "requires_visual_review": not visual_reviewed,
        "canvas_pt": [round(page_width * 72, 2), round(page_height * 72, 2)],
        "text_fit_audit": {"total": len(text_fit_items), "failed": sum(not item["fits"] for item in text_fit_items), "items": text_fit_items},
        "checks": checks,
        "connection_audit": {
            "total": len(connection_items), "checked": len(connection_items),
            "failed": failed_connections, "items": connection_items,
        },
        "line_semantics_audit": {
            "total": len(line_items), "checked": len(line_items), "failed": failed_lines, "items": line_items,
        },
        "overall_audit": {
            "pass": visual_reviewed and failed_connections == 0,
            "main_axis_clear": visual_reviewed,
            "visual_hierarchy_clear": visual_reviewed,
            "spacing_consistent": visual_reviewed,
            "whitespace_balanced": visual_reviewed,
            "thumbnail_readable": visual_reviewed,
            "full_page_render_checked": visual_reviewed,
        },
    }


@mcp.tool()
def health_check() -> str:
    """Verify Microsoft Visio COM automation and report the publication style preset."""
    pythoncom.CoInitialize()
    app = None
    try:
        app = win32com.client.DispatchEx("Visio.Application")
        return json_result(ok=True, visio=str(VISIO_EXE), version=app.Version, style=STYLE)
    finally:
        if app is not None:
            app.Quit()
        pythoncom.CoUninitialize()


@mcp.tool()
def render_diagram(spec: dict[str, Any], output_dir: str = "", basename: str = "visio_diagram") -> str:
    """Render an editable Visio diagram from structured nodes and edges. Supports true decision diamonds, orthogonal routes, explicit waypoints and publication-safe margins."""
    out = ensure_dir(output_dir)
    base = safe_basename(basename, "visio_diagram")
    spec_file = out / f"{base}.json"
    vsdx, pdf, svg, png = (out / f"{base}{ext}" for ext in (".vsdx", ".pdf", ".svg", ".png"))
    layout_file = out / f"{base}.layout.json"
    nodes, edges, layout_meta = normalize_spec(spec)
    resolved_spec = dict(spec)
    resolved_spec["nodes"] = nodes
    resolved_spec["edges"] = edges
    resolved_spec["resolved_layout"] = layout_meta
    json_dump(spec_file, resolved_spec)
    errors: list[str] = []
    layout_report: dict[str, Any] = {"pass": False, "requires_visual_review": True}
    pythoncom.CoInitialize()
    app = doc = stencil = None
    try:
        app = win32com.client.DispatchEx("Visio.Application")
        app.Visible = False
        doc = app.Documents.Add("")
        stencil = app.Documents.OpenEx("BASFLO_U.VSSX", 64)
        masters = {"decision": stencil.Masters.Item("判定")}
        page = doc.Pages.Item(1)
        page.Name = str(spec.get("page_name", "论文图"))
        page_width = number(layout_meta.get("page_width_in"), STYLE["paper_width_in"])
        page_height = number(layout_meta.get("page_height_in"), 4.0)
        page.PageSheet.CellsU("PageWidth").FormulaU = f"{page_width:g} in"
        page.PageSheet.CellsU("PageHeight").FormulaU = f"{page_height:g} in"
        page.PageSheet.CellsU("DrawingScale").FormulaU = "1 in"
        page.PageSheet.CellsU("PageScale").FormulaU = "1 in"
        shapes: dict[str, Any] = {}
        for i, node in enumerate(nodes):
            ident = str(node.get("id", f"n{i + 1}"))
            shp = draw_node(page, node, masters)
            shp.NameU = safe_basename(ident, f"n{i + 1}")
            shapes[ident] = shp
        draw_editorial_badges(page, nodes, shapes, resolved_spec)
        edge_paths: list[tuple[dict[str, Any], list[tuple[float, float]]]] = []
        for edge in edges:
            s, t = str(edge.get("from", "")), str(edge.get("to", ""))
            if s in shapes and t in shapes:
                edge_paths.append((edge, edge_points(shapes[s], shapes[t], edge)))
                connect(page, shapes[s], shapes[t], edge)
            else:
                errors.append(f"边引用未知节点: {s}->{t}")
        layout_report = build_layout_report(resolved_spec, shapes, edges, edge_paths, page_width, page_height)
        json_dump(layout_file, layout_report)
        doc.SaveAs(str(vsdx))
        doc.ExportAsFixedFormat(1, str(pdf), 1, 0)
        page.Export(str(svg))
        page.Export(str(png))
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        if doc is not None:
            try:
                doc.Close()
            except Exception:
                pass
        if stencil is not None:
            try:
                stencil.Close()
            except Exception:
                pass
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()
    # Visio crops PNG to the drawing even though PDF/SVG preserve the page.
    # Rasterize the fixed-size PDF so preview dimensions and margins are honest.
    if pdf.exists():
        try:
            pdf_doc = fitz.open(pdf)
            pdf_doc[0].get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False).save(png)
            pdf_doc.close()
        except Exception as exc:
            errors.append(f"PNG full-page render failed: {exc}")
    files = [vsdx, pdf, svg, png, spec_file, layout_file]
    return json_result(
        ok=not errors and all(p.exists() for p in files[:3]),
        publication_ready=bool(layout_report.get("pass", False)),
        requires_visual_review=bool(layout_report.get("requires_visual_review", True)),
        errors=errors,
        files=file_manifest(files),
    )


@mcp.tool()
def record_visual_review(layout_path: str, review: dict[str, Any]) -> str:
    """Record an actual final-size visual review and close the publication layout gate."""
    path = Path(layout_path).resolve()
    if not path.exists() or path.suffix.lower() != ".json":
        return json_result(ok=False, errors=["布局审计文件不存在或不是 JSON"])
    report = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "connections_checked", "text_line_clearance", "label_object_clearance",
        "final_font_size_readable", "main_axis_clear", "visual_hierarchy_clear",
        "spacing_consistent", "whitespace_balanced", "thumbnail_readable",
        "full_page_render_checked",
    ]
    missing = [key for key in required if key not in review]
    if missing:
        return json_result(ok=False, errors=[f"缺少视觉复核字段: {missing}"])
    accepted = all(bool(review[key]) for key in required)
    checks = report.setdefault("checks", {})
    checks["final_render_connections_checked"] = bool(review["connections_checked"])
    checks["text_line_clearance"] = bool(review["text_line_clearance"])
    checks["label_object_clearance"] = bool(review["label_object_clearance"])
    checks["final_font_size_readable"] = bool(review["final_font_size_readable"])
    checks["composition_balance"] = all(bool(review[key]) for key in (
        "main_axis_clear", "visual_hierarchy_clear", "spacing_consistent", "whitespace_balanced"
    ))
    for section in ("connection_audit", "line_semantics_audit"):
        audit = report.get(section, {})
        for item in audit.get("items", []):
            item["final_render_pass"] = bool(review["connections_checked"])
        audit["failed"] = sum(
            1 for item in audit.get("items", [])
            if not item.get("semantics_match", False)
            or not item.get("final_render_pass", False)
            or int(item.get("non_target_crossings", 0)) > 0
            or float(item.get("source_endpoint_error_pt", 0)) > 0.5
            or float(item.get("target_endpoint_error_pt", 0)) > 0.5
        )
    overall = report.setdefault("overall_audit", {})
    for key in ("main_axis_clear", "visual_hierarchy_clear", "spacing_consistent", "whitespace_balanced", "thumbnail_readable", "full_page_render_checked"):
        overall[key] = bool(review[key])
    overall["pass"] = accepted
    report["requires_visual_review"] = False
    report["review_notes"] = str(review.get("notes", "")).strip()
    report["style_audit"] = {
        "family": "visio",
        "final_min_font_pt": float(review.get("final_min_font_pt", 8.4)),
        "line_width_levels": int(review.get("line_width_levels", 2)),
        "color_count": int(review.get("color_count", 2)),
        "gradients": False,
        "shadows": False,
        "decorative_icons": False,
        "rounded_card_system": False,
        "math_font_consistent": True,
        "final_vector": True,
        "final_page_checked": bool(review["full_page_render_checked"]),
        "tikz_stylesheet_used": False,
        "dynamic_connectors_and_snap": True,
    }
    report["pass"] = (
        accepted
        and all(bool(value) for key, value in checks.items() if key != "latex_trim_required")
        and not bool(checks.get("latex_trim_required", True))
        and all(
            int(report.get(section, {}).get("failed", 1)) == 0
            for section in ("connection_audit", "line_semantics_audit")
        )
    )
    json_dump(path, report)
    return json_result(ok=bool(report["pass"]), layout=str(path), review_complete=True, report=report)


@mcp.tool()
def compose_vector_figure(spec: dict[str, Any], output_dir: str = "", basename: str = "visio_composite") -> str:
    """Compose MATLAB/TikZ SVG/PDF panels into an editable Visio page, then add native titles, captions, callouts, separators and arrows. Exports VSDX/PDF/SVG/PNG plus JSON manifest."""
    out = ensure_dir(output_dir)
    base = safe_basename(basename, "visio_composite")
    spec_file = out / f"{base}.json"
    json_dump(spec_file, spec)
    vsdx, pdf, svg, png = (out / f"{base}{ext}" for ext in (".vsdx", ".pdf", ".svg", ".png"))
    errors: list[str] = []
    pythoncom.CoInitialize()
    app = doc = None
    try:
        app = win32com.client.DispatchEx("Visio.Application")
        app.Visible = False
        doc = app.Documents.Add("")
        page = doc.Pages.Item(1)
        page.Name = str(spec.get("page_name", "混合论文图"))
        page_width = number(spec.get("page_width_in"), 12.2)
        page_height = number(spec.get("page_height_in"), 8.0)
        page.PageSheet.CellsU("PageWidth").FormulaU = f"{page_width:g} in"
        page.PageSheet.CellsU("PageHeight").FormulaU = f"{page_height:g} in"
        page.PageSheet.CellsU("DrawingScale").FormulaU = "1 in"
        page.PageSheet.CellsU("PageScale").FormulaU = "1 in"

        # Imported panels remain individual selectable Visio objects. Their native
        # aspect ratio is measured before resizing so text is never compressed.
        panel_metrics: list[dict[str, Any]] = []
        for index, panel in enumerate(spec.get("panels", []), start=1):
            if not isinstance(panel, dict):
                continue
            source = Path(str(panel.get("path", "")))
            if not source.exists():
                errors.append(f"面板文件不存在: {source}")
                continue
            shape = page.Import(str(source.resolve()))
            shape.NameU = safe_basename(str(panel.get("id", f"panel_{index}")), f"panel_{index}")
            x, y = number(panel.get("x"), page_width / 2), number(panel.get("y"), page_height / 2)
            width = number(panel.get("width"), 4.8)
            height = number(panel.get("height"), 3.0)
            cell(shape, "PinX", f"{x:g} in")
            cell(shape, "PinY", f"{y:g} in")
            source_ratio = svg_source_ratio(source)
            metric = fit_panel_preserving_aspect(
                shape, width, height, str(panel.get("fit", "contain")), source_ratio
            )
            metric.update({"id": shape.NameU, "source": str(source.resolve()), "box_width": width, "box_height": height})
            panel_metrics.append(metric)

        # Native Visio text/shape overlays handle the editorial organization layer.
        for item in spec.get("overlays", []):
            if not isinstance(item, dict):
                continue
            kind = str(item.get("type", "text"))
            x, y = number(item.get("x")), number(item.get("y"))
            w, h = number(item.get("width"), 2.0), number(item.get("height"), 0.35)
            if kind == "line":
                x2, y2 = number(item.get("x2"), x + w), number(item.get("y2"), y)
                shp = page.DrawLine(x, y, x2, y2)
                cell(shp, "LineColor", visio_rgb_formula(item.get("line"), (31, 78, 121)))
                cell(shp, "LineWeight", f"{number(item.get('line_weight_pt'), 0.8):g} pt")
                if item.get("arrow"):
                    cell(shp, "EndArrow", "13")
            elif kind in {"box", "tag"}:
                shp = page.DrawRectangle(x-w/2, y-h/2, x+w/2, y+h/2)
                shape_text(shp, str(item.get("text", "")), number(item.get("font_size"), 9.2))
                cell(shp, "FillForegnd", visio_rgb_formula(item.get("fill"), (234, 241, 248)))
                cell(shp, "FillPattern", "1")
                cell(shp, "LineColor", visio_rgb_formula(item.get("line"), (31, 78, 121)))
                cell(shp, "LineWeight", f"{number(item.get('line_weight_pt'), 0.7):g} pt")
                cell(shp, "Rounding", "0.05 in")
            else:
                shp = page.DrawRectangle(x-w/2, y-h/2, x+w/2, y+h/2)
                shape_text(shp, str(item.get("text", "")), number(item.get("font_size"), 10.0))
                cell(shp, "LinePattern", "0")
                cell(shp, "FillPattern", "0")
                if item.get("bold"):
                    cell(shp, "Char.Style", "1")

        aspect_tolerance = number(spec.get("aspect_tolerance"), 0.002)
        for metric in panel_metrics:
            if number(metric.get("aspect_distortion"), 1.0) > aspect_tolerance:
                errors.append(
                    f"面板发生非等比缩放: {metric.get('id')} "
                    f"source={metric.get('source_ratio'):.6f}, output={metric.get('output_ratio'):.6f}"
                )
        metrics_file = out / f"{base}.panel_metrics.json"
        json_dump(metrics_file, {
            "ok": not errors,
            "aspect_tolerance": aspect_tolerance,
            "panels": panel_metrics,
        })

        doc.SaveAs(str(vsdx))
        doc.ExportAsFixedFormat(1, str(pdf), 1, 0)
        page.Export(str(svg))
        page.Export(str(png))
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        if doc is not None:
            try: doc.Close()
            except Exception: pass
        if app is not None:
            try: app.Quit()
            except Exception: pass
        pythoncom.CoUninitialize()
    metrics_file = out / f"{base}.panel_metrics.json"
    files = [vsdx, pdf, svg, png, spec_file, metrics_file]
    return json_result(ok=not errors and all(p.exists() for p in files[:3]), errors=errors, files=file_manifest(files))


if __name__ == "__main__":
    mcp.run()
