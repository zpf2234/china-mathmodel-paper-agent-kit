from __future__ import annotations

"""Structured A/B signature-figure benchmarks rendered through the MATLAB MCP backend.

These are cross-problem archetypes, not expected answers for any contest problem.  Every
benchmark has an evidence linkage contract; palette-only restyling and decorative panel
collages are rejected before MATLAB is invoked.
"""

import json
import re
from pathlib import Path
from typing import Any

import fitz

import matlab_server

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "benchmarks" / "signature_specs"
OUT = ROOT / "signature_benchmark_outputs"

REQUIRED_KINDS = {
    "a_mechanism_result": {"mechanism", "event_series", "closure_series"},
    "b_strategy_landscape": {"x", "y", "value", "strategy"},
    "uncertainty_decision_linkage": {"sample_size", "uncertainty", "policy_values", "switches"},
}


def validate_signature_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    kind = spec.get("kind")
    if kind not in REQUIRED_KINDS:
        return [f"unsupported signature benchmark kind: {kind}"]
    for field in ("core_claim", "ten_second_takeaway"):
        if not isinstance(spec.get(field), str) or len(spec[field].strip()) < 8:
            errors.append(f"{field} must be substantive")
    order = spec.get("read_order")
    if not isinstance(order, list) or not 2 <= len(order) <= 5 or any(not isinstance(x, str) or len(x.strip()) < 2 for x in order):
        errors.append("read_order must contain 2..5 semantic steps")
    linkage = spec.get("data_linkage")
    if not isinstance(linkage, dict):
        errors.append("data_linkage must be an object")
    else:
        for field in ("source_fields", "element_links"):
            values = linkage.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(x, str) or len(x.strip()) < 2 for x in values):
                errors.append(f"data_linkage.{field} must be non-empty")
    checks = spec.get("signature_checks")
    if not isinstance(checks, dict):
        errors.append("signature_checks must be an object")
    else:
        for field in ("integrated_narrative", "adds_explanatory_responsibility", "not_palette_only", "not_decorative_collage"):
            if checks.get(field) is not True:
                errors.append(f"signature_checks.{field} must be true")
    evidence = spec.get("evidence")
    missing = REQUIRED_KINDS[kind] - set(evidence) if isinstance(evidence, dict) else REQUIRED_KINDS[kind]
    if missing:
        errors.append(f"evidence missing fields: {sorted(missing)}")
    elif kind == "a_mechanism_result":
        mechanism = evidence.get("mechanism", {})
        closure = evidence.get("closure_series", {})
        if not isinstance(mechanism.get("boundary_equation"), str) or len(mechanism["boundary_equation"].strip()) < 4:
            errors.append("mechanism boundary_equation must be explicit")
        if not isinstance(closure.get("error_definition"), str) or len(closure["error_definition"].strip()) < 6:
            errors.append("closure_series.error_definition must identify the verified quantity")
        if not isinstance(closure.get("report_threshold"), (int, float)):
            errors.append("closure_series.report_threshold must be numeric")
    elif kind == "b_strategy_landscape":
        x, y = evidence.get("x", []), evidence.get("y", [])
        value, strategy = evidence.get("value", []), evidence.get("strategy", [])
        if len(value) != len(y) or len(strategy) != len(y) or any(len(row) != len(x) for row in value + strategy):
            errors.append("strategy landscape grids must match x/y dimensions")
        if len({cell for row in strategy for cell in row}) < 2:
            errors.append("strategy landscape must contain a real switching boundary")
    elif kind == "uncertainty_decision_linkage":
        switches = evidence.get("switches", [])
        if not isinstance(switches, list) or not switches:
            errors.append("uncertainty linkage requires switch events")
        else:
            for switch in switches:
                if not isinstance(switch, dict) or not isinstance(switch.get("n"), (int, float)) or not isinstance(switch.get("uncertainty_threshold"), (int, float)):
                    errors.append("each switch must bind n to a numeric uncertainty_threshold")
                    break
    return errors


def mvec(values: list[float]) -> str:
    return "[" + " ".join(f"{float(value):.10g}" for value in values) + "]"


def mmat(rows: list[list[float]]) -> str:
    return "[" + ";".join(" ".join(f"{float(value):.10g}" for value in row) for row in rows) + "]"


def preamble(width: float = 15.5, height: float = 8.8) -> list[str]:
    return [
        "set(groot,'defaultFigureColor','w');",
        "set(groot,'defaultAxesFontName','Microsoft YaHei','defaultTextFontName','Microsoft YaHei');",
        f"fig=figure('Visible','off','Units','centimeters','Position',[2 2 {width:.3f} {height:.3f}]);",
        "blue=[0.2078 0.3608 0.4902]; teal=[0.1647 0.6157 0.5608]; orange=[0.8510 0.5098 0.3294]; ink=[0.19 0.21 0.23]; pale=[0.93 0.95 0.96];",
    ]


def finish(base: str, width: float = 15.5, height: float = 8.8, output_dir: Path | None = None) -> list[str]:
    out = (output_dir or OUT).as_posix().replace("'", "''")
    return [
        f"set(fig,'PaperUnits','centimeters','PaperPosition',[0 0 {width:.3f} {height:.3f}],'PaperSize',[{width:.3f} {height:.3f}]);",
        f"print(fig,'{out}/{base}.pdf','-dpdf','-painters');",
        f"print(fig,'{out}/{base}.svg','-dsvg');",
        f"exportgraphics(fig,'{out}/{base}.png','Resolution',450,'BackgroundColor','white');",
        "close(fig);",
    ]


def mechanism_script(spec: dict[str, Any], base: str, output_dir: Path | None = None) -> str:
    ev = spec["evidence"]
    t = ev["event_series"]["x"]
    margin = ev["event_series"]["boundary_margin"]
    response = ev["event_series"]["response"]
    resolution = ev["closure_series"]["resolution"]
    error = ev["closure_series"]["error"]
    threshold = float(ev["closure_series"]["report_threshold"])
    error_definition = str(ev["closure_series"]["error_definition"]).replace("'", "''")
    boundary_equation = str(ev["mechanism"]["boundary_equation"]).replace("'", "''")
    event = ev["event_series"]["critical_x"]
    lines = preamble()
    lines += [
        "tl=tiledlayout(fig,1,3,'TileSpacing','loose','Padding','compact');",
        "ax1=nexttile(tl,1); hold(ax1,'on'); axis(ax1,'equal'); axis(ax1,[0 5 0 4]); axis(ax1,'off');",
        "patch(ax1,[.5 4.5 4.5 .5],[.55 .55 .85 .85],pale,'EdgeColor','none');",
        "plot(ax1,[.7 4.25],[.9 3.15],'-','Color',blue,'LineWidth',1.5);",
        "plot(ax1,[.7 4.25],[3.15 .9],'--','Color',ink,'LineWidth',.9);",
        "plot(ax1,2.47,2.03,'o','Color',orange,'MarkerFaceColor',orange,'MarkerSize',6);",
        "quiver(ax1,2.47,2.03,0,-.85,0,'Color',orange,'LineWidth',1.2,'MaxHeadSize',.55);",
        "text(ax1,.7,3.55,'(a) 机理定义','FontSize',8.5,'FontWeight','bold','Color',ink);",
        f"text(ax1,.7,3.20,'{boundary_equation}','FontSize',8,'Color',blue,'Interpreter','none');",
        "text(ax1,2.64,2.20,'临界构型 x_c','FontSize',8,'Color',orange);",
        "text(ax1,.65,.22,'边界交会定义同一临界事件','FontSize',7.4,'Color',ink);",
        f"ax2=nexttile(tl,2); hold(ax2,'on'); t={mvec(t)}; margin={mvec(margin)}; response={mvec(response)};",
        "yyaxis(ax2,'left'); plot(ax2,t,margin,'-','Color',blue,'LineWidth',1.25); yline(ax2,0,':','Color',ink,'HandleVisibility','off'); ylabel(ax2,'边界余量');",
        "yyaxis(ax2,'right'); plot(ax2,t,response,'-','Color',teal,'LineWidth',1.25);",
        f"xline(ax2,{float(event):.10g},'--','Color',orange,'LineWidth',1.1,'HandleVisibility','off'); text(ax2,{float(event)+.18:.10g},.57,'t_c = {float(event):.2f} s','Color',orange,'FontSize',7.5);",
        "text(ax2,t(1),.95,'(b) 事件检测：g(t_c)=0','Color',ink,'FontSize',8,'FontWeight','bold'); text(ax2,t(end)*.52,.88,'青绿：状态响应','Color',teal,'FontSize',7.3);",
        "xlabel(ax2,'时间 / s'); grid(ax2,'on'); ax2.GridAlpha=.08; ax2.FontSize=8; box(ax2,'on');",
        f"ax3=nexttile(tl,3); hold(ax3,'on'); r={mvec(resolution)}; e={mvec(error)}; loglog(ax3,r,e,'-o','Color',blue,'MarkerFaceColor','w','LineWidth',1.2,'MarkerSize',4);",
        f"yline(ax3,{threshold:.10g},':','阈值 {threshold:.1e}','Color',orange,'LineWidth',1,'LabelHorizontalAlignment','left','HandleVisibility','off'); grid(ax3,'on'); ax3.GridAlpha=.08; box(ax3,'on'); ax3.FontSize=8;",
        f"xlabel(ax3,'分辨率'); ylabel(ax3,'{error_definition}','Interpreter','none'); text(ax3,r(1),max(e)*.72,'(c) 独立误差闭合','Color',ink,'FontSize',8,'FontWeight','bold'); text(ax3,r(end-1),e(end-1)*1.6,'低于报告阈值','Color',orange,'FontSize',7.5);",
    ]
    lines += finish(base, output_dir=output_dir)
    return "\n".join(lines) + "\n"


def landscape_script(spec: dict[str, Any], base: str, output_dir: Path | None = None) -> str:
    ev = spec["evidence"]
    x, y, value, strategy = ev["x"], ev["y"], ev["value"], ev["strategy"]
    cx, cy = ev["current"]
    rx, ry = ev["recommended"]
    lines = preamble()
    lines += [
        "tl=tiledlayout(fig,1,4,'TileSpacing','compact','Padding','compact');",
        f"x={mvec(x)}; y={mvec(y)}; V={mmat(value)}; S={mmat(strategy)}; [X,Y]=meshgrid(x,y);",
        "ax1=nexttile(tl,[1 3]); hold(ax1,'on'); cmap=[.87 .91 .94;.82 .93 .90;.97 .89 .82]; colormap(ax1,cmap); contourf(ax1,X,Y,S,[.5 1.5 2.5 3.5],'LineColor','none');",
        "[c,h]=contour(ax1,X,Y,V,7,'LineColor',[.42 .45 .47],'LineWidth',.55); clabel(c,h,'FontSize',7,'Color',ink,'LabelSpacing',420);",
        f"plot(ax1,{float(cx):.10g},{float(cy):.10g},'o','Color',ink,'MarkerFaceColor','w','MarkerSize',6,'LineWidth',1.1);",
        f"plot(ax1,{float(rx):.10g},{float(ry):.10g},'p','Color',orange,'MarkerFaceColor',orange,'MarkerSize',9);",
        f"text(ax1,{float(cx):.10g},{float(cy):.10g},'  当前：策略 A','FontSize',8,'Color',ink);",
        f"text(ax1,{float(rx):.10g},{float(ry):.10g},'  推荐：策略 B','FontSize',8,'Color',orange);",
        "xlabel(ax1,'需求水平'); ylabel(ax1,'风险权重'); box(ax1,'on'); ax1.FontSize=8; xlim(ax1,[x(1) x(end)]); ylim(ax1,[y(1) y(end)+.05*(y(end)-y(1))]);",
        "contour(ax1,X,Y,S,[1.5 2.5],'LineColor',ink,'LineWidth',1.35);",
        "text(ax1,.76,.12,'策略 A','FontSize',8,'Color',ink); text(ax1,1.12,.27,'策略 B','FontSize',8,'Color',ink); text(ax1,1.34,.78,'策略 C','FontSize',8,'Color',ink);",
        "text(ax1,x(1)+.02*(x(end)-x(1)),y(end)-.04*(y(end)-y(1)),'最优策略区（底色）·价值等高线·切换边界（粗线）','FontSize',7.8,'Color',ink,'VerticalAlignment','top');",
        "ax2=nexttile(tl,4); vals=[max(V(S==1)) max(V(S==2)) max(V(S==3))]; barh(ax2,1:3,vals,.55,'FaceColor',blue,'EdgeColor','none');",
        "ax2.YTick=1:3; ax2.YTickLabel={'策略 A','策略 B','策略 C'}; xlabel(ax2,'区域最优价值'); ax2.FontSize=8; box(ax2,'on'); grid(ax2,'on'); ax2.GridAlpha=.08;",
        "[best,idx]=max(vals); hold(ax2,'on'); plot(ax2,best,idx,'p','Color',orange,'MarkerFaceColor',orange,'MarkerSize',8);",
    ]
    lines += finish(base, output_dir=output_dir)
    return "\n".join(lines) + "\n"


def uncertainty_script(spec: dict[str, Any], base: str, output_dir: Path | None = None) -> str:
    ev = spec["evidence"]
    n = ev["sample_size"]
    uncertainty = ev["uncertainty"]
    names = list(ev["policy_values"])
    switches = ev["switches"]
    lines = preamble()
    lines += [
        "tl=tiledlayout(fig,2,1,'TileSpacing','compact','Padding','compact');",
        f"n={mvec(n)}; u={mvec(uncertainty)}; ax1=nexttile(tl,1); plot(ax1,n,u,'-o','Color',blue,'MarkerFaceColor','w','LineWidth',1.2,'MarkerSize',3.5);",
        "hold(ax1,'on'); ylabel(ax1,'不确定性上界 U(n)'); grid(ax1,'on'); ax1.GridAlpha=.08; box(ax1,'on'); ax1.FontSize=8;",
        "text(ax1,n(2),u(2)*1.08,'(a) 信息增加，不确定性收缩','Color',ink,'FontSize',8,'FontWeight','bold');",
        "ax2=nexttile(tl,2); hold(ax2,'on');",
    ]
    colors = ["blue", "teal", "orange"]
    for index, name in enumerate(names):
        lines.append(f"v{index+1}={mvec(ev['policy_values'][name])}; h{index+1}=plot(ax2,n,v{index+1},'-','Color',{colors[index % len(colors)]},'LineWidth',1.2,'DisplayName','{name}');")
    for switch in switches:
        lines.append(f"yline(ax1,{float(switch['uncertainty_threshold']):.10g},':','U={float(switch['uncertainty_threshold']):.3f}','Color',orange,'LineWidth',.8,'HandleVisibility','off');")
        lines.append(f"xline(ax1,{float(switch['n']):.10g},'--','Color',ink,'LineWidth',.8,'HandleVisibility','off'); xline(ax2,{float(switch['n']):.10g},'--','Color',ink,'LineWidth',.8,'HandleVisibility','off');")
        lines.append(f"text(ax2,{float(switch['n'])+3:.10g},72,'{switch['label']}','Color',ink,'FontSize',7.0,'Rotation',0,'VerticalAlignment','top');")
    lines += [
        "xlabel(ax2,'样本量 n'); ylabel(ax2,'稳健价值'); grid(ax2,'on'); ax2.GridAlpha=.08; box(ax2,'on'); ax2.FontSize=8; legend(ax2,[h1 h2 h3],{'保守策略','均衡策略','进取策略'},'Location','southeast','Box','off','FontSize',8);",
        "linkaxes([ax1 ax2],'x'); text(ax2,n(1),74,'(b) 风险阈值穿越 → 策略价值占优','Color',ink,'FontSize',8,'FontWeight','bold');",
    ]
    lines += finish(base, output_dir=output_dir)
    return "\n".join(lines) + "\n"


BUILDERS = {
    "a_mechanism_result": mechanism_script,
    "b_strategy_landscape": landscape_script,
    "uncertainty_decision_linkage": uncertainty_script,
}


def _svg_length_cm(value: str) -> float | None:
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(cm|mm|in|pt|px)?\s*", value)
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2) or "px"
    factors = {"cm": 1.0, "mm": 0.1, "in": 2.54, "pt": 2.54 / 72.0, "px": 2.54 / 96.0}
    return number * factors[unit]


def audit_rendered_signature(pdf_path: Path, svg_path: Path, width_cm: float = 15.5, height_cm: float = 8.8) -> dict[str, Any]:
    """Machine-check objective render facts only; never infer subjective visual quality."""
    errors: list[str] = []
    pdf_info: dict[str, Any] = {}
    svg_info: dict[str, Any] = {}
    if not pdf_path.exists() or not svg_path.exists():
        return {"pass": False, "errors": ["required PDF/SVG render missing"], "pdf": pdf_info, "svg": svg_info}

    doc = fitz.open(pdf_path)
    if doc.page_count != 1:
        errors.append("PDF must contain exactly one page")
    if doc.page_count:
        page = doc[0]
        expected_ratio = width_cm / height_cm
        actual_ratio = page.rect.width / page.rect.height
        ratio_distortion = abs(actual_ratio / expected_ratio - 1.0)
        embedded_images = len(doc.get_page_images(0, full=True))
        drawing_count = len(page.get_drawings())
        text_chars = len(page.get_text().strip())
        pdf_info = {
            "pages": doc.page_count,
            "width_pt": round(page.rect.width, 3),
            "height_pt": round(page.rect.height, 3),
            "page_size_distortion": ratio_distortion,
            "embedded_images": embedded_images,
            "drawing_count": drawing_count,
            "text_chars": text_chars,
        }
        if ratio_distortion > 0.002:
            errors.append(f"PDF aspect-ratio distortion {ratio_distortion:.6f} exceeds 0.002")
        if embedded_images:
            errors.append(f"PDF contains {embedded_images} embedded raster image(s)")
        if drawing_count == 0 and text_chars == 0:
            errors.append("PDF has no inspectable vector/text content")
    doc.close()

    svg_text = svg_path.read_text(encoding="utf-8", errors="replace")
    root_match = re.search(r"<svg\b([^>]*)>", svg_text, re.IGNORECASE)
    attrs = root_match.group(1) if root_match else ""
    width_match = re.search(r'\bwidth=["\']([^"\']+)', attrs, re.IGNORECASE)
    height_match = re.search(r'\bheight=["\']([^"\']+)', attrs, re.IGNORECASE)
    width = _svg_length_cm(width_match.group(1)) if width_match else None
    height = _svg_length_cm(height_match.group(1)) if height_match else None
    svg_ratio_distortion = abs((width / height) / (width_cm / height_cm) - 1.0) if width and height else None
    raster_images = len(re.findall(r"<image\b", svg_text, re.IGNORECASE))
    svg_info = {
        "width_cm": width,
        "height_cm": height,
        "aspect_ratio_distortion": svg_ratio_distortion,
        "embedded_raster_images": raster_images,
        "microsoft_yahei_declared": "Microsoft YaHei" in svg_text,
    }
    if svg_ratio_distortion is None:
        errors.append("SVG width/height are not measurable")
    elif svg_ratio_distortion > 0.002:
        errors.append(f"SVG aspect-ratio distortion {svg_ratio_distortion:.6f} exceeds 0.002")
    if raster_images:
        errors.append(f"SVG contains {raster_images} embedded raster image(s)")
    return {"pass": not errors, "errors": errors, "pdf": pdf_info, "svg": svg_info}


def render_one(path: Path) -> dict[str, Any]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_signature_spec(spec)
    if errors:
        return {"ok": False, "errors": errors, "spec": str(path)}
    OUT.mkdir(parents=True, exist_ok=True)
    base = path.stem
    (OUT / f"{base}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    result = json.loads(matlab_server.run_script(BUILDERS[spec["kind"]](spec, base, OUT), str(OUT), base))
    required = [OUT / f"{base}{suffix}" for suffix in (".pdf", ".svg", ".png", ".m", ".json")]
    artifact_ok = all(output.exists() and output.stat().st_size > 0 for output in required)
    render_audit = audit_rendered_signature(OUT / f"{base}.pdf", OUT / f"{base}.svg") if artifact_ok else {
        "pass": False,
        "errors": ["render outputs incomplete"],
    }
    result["ok"] = result.get("ok") is True and artifact_ok and render_audit["pass"]
    result["errors"] = render_audit.get("errors", [])
    result["render_audit"] = render_audit
    result["benchmark_spec"] = spec
    result["required_outputs"] = [str(output) for output in required]
    return result


def main() -> int:
    paths = sorted(SPEC_DIR.glob("*.json"))
    results = {path.stem: render_one(path) for path in paths}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "signature_benchmark_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {name: {"ok": value.get("ok"), "errors": value.get("errors", [])} for name, value in results.items()}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if len(results) >= 3 and all(value.get("ok") for value in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
