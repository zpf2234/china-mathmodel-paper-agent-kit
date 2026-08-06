#!/usr/bin/env python
"""Deterministic CUMCM figure necessity, type, and MCP backend router."""
from __future__ import annotations
import argparse, json
from pathlib import Path

NO_FIGURE_SECTIONS = {"问题重述", "模型假设", "符号说明", "参考文献", "附录"}
DATA_TYPES = {
    "time_series": "time_response", "iteration": "convergence",
    "xy_relation": "scatter_fit", "distribution": "distribution_comparison",
    "groups": "ranked_comparison", "parameter_scan_1d": "sensitivity_curve",
    "parameter_scan_2d": "contour", "matrix": "heatmap",
    "spatial_path": "trajectory", "spatial_state": "configuration",
    "field_2d": "contour", "field_3d": "surface", "uncertainty": "uncertainty_band",
}

def route(item: dict) -> dict:
    reasons=[]
    section=str(item.get("section", ""))
    claim=str(item.get("claim", "")).strip()
    if not claim or not item.get("claim_id"):
        return {"should_insert":False,"renderer":None,"figure_type":None,"reasons":["缺少唯一 claim 或 claim_id"],"status":"REJECT"}
    if item.get("existing_figure_overlap"):
        return {"should_insert":False,"renderer":None,"figure_type":None,"reasons":["与现有图重复"],"status":"REJECT"}
    simple = int(item.get("step_count",0)) <= 2 and not any(item.get(k) for k in ("has_geometry","has_decision","has_loop","has_spatial_coordinates")) and not item.get("data_shape")
    if section in NO_FIGURE_SECTIONS and simple:
        return {"should_insert":False,"renderer":None,"figure_type":None,"reasons":["章节默认不需要正式论证图且过程简单"],"status":"REJECT"}

    renderer=None; ftype=None
    if item.get("has_decision") or item.get("has_loop") or int(item.get("step_count",0)) >= 3:
        renderer="paper-visio"; ftype="decision_flow" if item.get("has_decision") else "algorithm_flow"
        reasons.append("存在判断/循环/三个以上阶段")
    elif item.get("has_geometry") or item.get("needs_exact_labels"):
        renderer="paper-tikz"; ftype="geometry_mechanism"
        reasons.append("精确几何、角度、尺寸或公式标注")
    elif item.get("has_spatial_coordinates") or item.get("data_shape") in DATA_TYPES:
        renderer="paper-matlab"; ftype=DATA_TYPES.get(item.get("data_shape"),"trajectory")
        reasons.append("真实数值、轨迹、状态或统计证据")
    elif int(item.get("object_count",0)) >= 3:
        renderer="paper-visio"; ftype="problem_relation"
        reasons.append("三个以上对象存在关系")
    else:
        return {"should_insert":False,"renderer":None,"figure_type":None,"reasons":["文字或表格可充分表达"],"status":"REJECT"}

    section_kind = "validation" if "验证" in section else ("analysis" if "分析" in section else "model")
    insertion = {
        "analysis":"共享关系说明之后",
        "model":"对象与坐标定义之后、首个控制方程之前",
        "validation":"提出待检验命题之后、关键读数与解释之前",
    }[section_kind]
    return {
        "should_insert":True,"renderer":renderer,"figure_type":ftype,"reasons":reasons,"status":"ROUTED",
        "insertion_point":insertion,
        "before_sentence_contract":"图前提出对象、条件和待读数，不提前宣布结论",
        "after_paragraph_contract":"图后依次写观察、关键数值、机制解释和对当前答案的影响",
        "required_artifacts":["spec_json","editable_source","pdf","svg","png_preview","provenance","final_page_review"],
    }

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    src=Path(a.input); data=json.loads(src.read_text(encoding="utf-8")); items=data if isinstance(data,list) else data.get("figures",[])
    out=[]
    for item in items:
        r=route(item); r.update({"figure_id":item.get("figure_id"),"claim_id":item.get("claim_id"),"claim":item.get("claim"),"section":item.get("section")}); out.append(r)
    result={"schema_version":1,"router_mode":"deterministic_fallback","pass":all(x["status"] in {"ROUTED","REJECT"} for x in out),"figures":out}
    p=Path(a.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"pass":result["pass"],"routed":sum(x["should_insert"] for x in out),"rejected":sum(not x["should_insert"] for x in out),"output":str(p)},ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
