from __future__ import annotations

import json
from pathlib import Path

import matlab_server
import tikz_server
import visio_server

OUT = Path(__file__).resolve().parent / "benchmark_outputs"
OUT.mkdir(parents=True, exist_ok=True)

matlab_spec = {
    "kind": "line2d",
    "title": "两种算法迭代收敛曲线对比",
    "show_title": False,
    "xlabel": "迭代次数 k",
    "ylabel": "归一化目标函数值",
    "threshold": 0.25,
    "threshold_label": "判停阈值 = 0.25",
    "xlim": [0.7, 12.3],
    "ylim": [0.16, 1.04],
    "series": [
        {"name": "改进算法", "x": list(range(1, 13)), "y": [1.00, 0.72, 0.53, 0.41, 0.33, 0.28, 0.245, 0.221, 0.208, 0.201, 0.198, 0.197], "markers": True},
        {"name": "基准算法", "x": list(range(1, 13)), "y": [1.00, 0.85, 0.73, 0.64, 0.56, 0.50, 0.45, 0.41, 0.38, 0.355, 0.337, 0.325], "markers": True},
    ],
    "annotations": [
        {"x": 7, "y": 0.245, "text": "k=7，f=0.245，达到阈值", "dx": 0.55, "dy": 0.08},
        {"x": 12, "y": 0.325, "text": "k=12，f=0.325，仍未达到阈值", "dx": -3.55, "dy": 0.10},
    ],
}

tikz_spec = {
    "title": "",
    "elements": [
        {"type": "line", "from": [0, 0], "to": [7, 0], "style": "paperline"},
        {"type": "line", "from": [0, 0], "to": [5.5, 3.2], "style": "paperline"},
        {"type": "line", "from": [5.5, 3.2], "to": [7, 0], "style": "accentline,dashed"},
        {"type": "circle", "center": [0, 0], "radius": 0.07, "style": "paperline,fill=paperblue"},
        {"type": "circle", "center": [7, 0], "radius": 0.07, "style": "paperline,fill=paperblue"},
        {"type": "circle", "center": [5.5, 3.2], "radius": 0.09, "style": "accentline,fill=paperorange"},
        {"type": "line", "from": [0, -0.08], "to": [0, -1.10], "style": "draw=black!45,dashed,line width=0.55pt"},
        {"type": "line", "from": [7, -0.08], "to": [7, -1.10], "style": "draw=black!45,dashed,line width=0.55pt"},
        {"type": "node", "at": [-0.25, -0.38], "text": "$O$", "options": ""},
        {"type": "node", "at": [7.24, -0.38], "text": "$B$", "options": ""},
        {"type": "node", "at": [5.5, 3.52], "text": "$A$", "options": ""},
        {"type": "node", "at": [6.55, 1.82], "text": "约束边 $|AB|=d$", "options": "paperlabel"},
        {"type": "angle", "vertex": [0, 0], "radius": 0.9, "start_angle": 0, "end_angle": 30.2, "label": "$\\theta$"},
        {"type": "dimension", "from": [0, -1.05], "to": [7, -1.05], "label": "$L=|OB|$"},
    ],
}

visio_spec = {
    "page_name": "算法技术路线",
    "page_width_in": 6.10,
    "strict_audit": True,
    "visual_reviewed": False,
    "nodes": [
        {"id": "start", "type": "start", "text": "输入实验数据与边界条件"},
        {"id": "prep", "type": "process", "text": "异常诊断与量纲统一"},
        {"id": "model", "type": "process", "text": "建立机理约束优化模型"},
        {"id": "solve", "type": "process", "text": "自适应搜索与参数更新"},
        {"id": "judge", "type": "decision", "text": "误差小于阈值？"},
        {"id": "update", "type": "process", "text": "更新种群与惩罚系数"},
        {"id": "verify", "type": "process", "text": "敏感性与样本外验证"},
        {"id": "end", "type": "end", "text": "输出最优方案及置信区间"},
    ],
    "edges": [
        {"id": "e01", "from": "start", "to": "prep", "meaning": "输入数据进入预处理"},
        {"id": "e02", "from": "prep", "to": "model", "meaning": "统一量纲后的数据进入模型"},
        {"id": "e03", "from": "model", "to": "solve", "meaning": "模型约束传递给搜索过程"},
        {"id": "e04", "from": "solve", "to": "judge", "meaning": "候选解进入误差判定"},
        {"id": "e05", "kind": "decision_branch", "from": "judge", "to": "verify", "label": "是", "meaning": "误差达标后进入验证"},
        {"id": "e06", "kind": "decision_branch", "from": "judge", "to": "update", "label": "否", "meaning": "误差未达标时更新参数"},
        {"id": "e07", "kind": "feedback_loop", "from": "update", "to": "solve", "label": "迭代", "dashed": True, "feedback": True, "meaning": "更新参数后重新搜索"},
        {"id": "e08", "from": "verify", "to": "end", "meaning": "验证通过后输出结果"},
    ],
}

def main() -> int:
    results = {
        "matlab": json.loads(matlab_server.render_figure(matlab_spec, str(OUT), "benchmark_matlab_convergence")),
        "tikz": json.loads(tikz_server.render_geometry(tikz_spec, str(OUT), "benchmark_tikz_geometry")),
        "visio": json.loads(visio_server.render_diagram(visio_spec, str(OUT), "benchmark_visio_flowchart")),
    }
    (OUT / "benchmark_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: {"ok": v.get("ok"), "files": v.get("files", []), "errors": v.get("errors", [])} for k, v in results.items()}, ensure_ascii=False, indent=2))
    return 0 if all(v.get("ok") for v in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
