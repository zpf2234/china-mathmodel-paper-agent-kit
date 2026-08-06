from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "CUMCM Paper Figure Router",
    instructions=(
        "Decide whether a CUMCM paper needs a figure, select Visio, TikZ or MATLAB, "
        "and return the exact insertion contract before any renderer is called."
    ),
)


FORBIDDEN_SECTIONS = {"abstract", "restatement", "assumptions", "notation", "references", "appendix"}
SECTION_ALIASES = {
    "摘要": "abstract",
    "问题重述": "restatement",
    "问题分析": "analysis",
    "模型假设": "assumptions",
    "符号说明": "notation",
    "模型的建立与求解": "model",
    "建模求解": "model",
    "结果": "results",
    "结果验证": "validation",
    "验证": "validation",
    "模型评价": "evaluation",
    "参考文献": "references",
    "附录": "appendix",
}


def _section(value: Any) -> str:
    text = str(value or "").strip()
    return SECTION_ALIASES.get(text, text.lower())


def _bool(data: dict[str, Any], key: str) -> bool:
    return bool(data.get(key, False))


def _int(data: dict[str, Any], key: str) -> int:
    try:
        return int(data.get(key, 0))
    except (TypeError, ValueError):
        return 0


def _reject(reason: str, section: str, claim: str) -> dict[str, Any]:
    return {
        "should_insert": False,
        "section": section,
        "claim": claim,
        "reason": reason,
        "renderer": "none",
        "figure_type": "none",
        "insertion_point": "none",
        "required_inputs": [],
        "before_sentence_contract": "",
        "after_paragraph_contract": "",
    }


def decide(spec: dict[str, Any]) -> dict[str, Any]:
    section = _section(spec.get("section"))
    claim = str(spec.get("claim", "")).strip()
    if not claim:
        return _reject("没有唯一待证明命题，不能用图形替代尚未定义的论证职责", section, claim)
    if section in FORBIDDEN_SECTIONS:
        return _reject("该章节只承担文字、假设、符号或文献职责，正式图形移至分析、模型、结果或验证部分", section, claim)
    if bool(spec.get("duplicates_existing_figure", False)):
        return _reject("与现有图形承担相同证据职责，应合并或删除重复图", section, claim)

    geometry = spec.get("geometry") if isinstance(spec.get("geometry"), dict) else {}
    data = spec.get("data") if isinstance(spec.get("data"), dict) else {}
    relations = spec.get("relations") if isinstance(spec.get("relations"), dict) else {}
    steps = _int(relations, "steps")
    branches = _int(relations, "branches")
    feedback = _bool(relations, "feedback")
    shared_outputs = _int(relations, "shared_outputs")
    object_count = _int(relations, "object_count")

    has_exact_geometry = any(
        _bool(geometry, key)
        for key in ("coordinates", "angles", "tangency", "projection", "collision_boundary", "dimensions")
    )
    has_computed_data = any(
        _bool(data, key)
        for key in ("time_series", "trajectory", "surface", "matrix", "distribution", "comparison", "sensitivity", "uncertainty")
    )

    if section == "analysis" and shared_outputs >= 1 and object_count >= 3:
        renderer, figure_type = "paper-visio", "problem_relation"
        insertion = "问题分析章末，在各问依赖与共享量说明之后"
        required = ["逐问输入输出", "共享变量或模型", "每条关系边的传递语义"]
    elif has_exact_geometry and section in {"analysis", "model"}:
        renderer, figure_type = "paper-tikz", "geometry_mechanism"
        insertion = "对应模型小节中，坐标系和对象定义之后、首个控制方程之前"
        required = ["命名坐标", "几何约束", "正文符号", "有向与无向线语义"]
    elif (branches >= 1 or feedback) and steps >= 3 and section in {"analysis", "model"}:
        renderer, figure_type = "paper-visio", "algorithm_flow"
        insertion = "对应求解小节中，算法状态与判停条件定义之后、参数设置或结果之前"
        required = ["步骤清单", "判断条件", "分支去向", "反馈更新节点"]
    elif steps >= 3 and section == "model" and object_count >= 3:
        renderer, figure_type = "paper-visio", "module_structure"
        insertion = "共享模型或模块定义之后、各模块公式展开之前"
        required = ["模块输入输出", "关系方向", "共享变量"]
    elif has_computed_data and section in {"results", "validation", "model"}:
        renderer = "paper-matlab"
        if _bool(data, "time_series"):
            figure_type = "time_response"
        elif _bool(data, "trajectory"):
            figure_type = "trajectory"
        elif _bool(data, "surface") or _bool(data, "matrix"):
            figure_type = "parameter_field"
        elif _bool(data, "sensitivity") or _bool(data, "uncertainty"):
            figure_type = "validation_sensitivity"
        elif _bool(data, "distribution"):
            figure_type = "distribution_diagnostic"
        else:
            figure_type = "quantitative_comparison"
        insertion = "提出待检验命题的引导句之后、关键数值与机理解释之前"
        required = ["结构化结果数据", "变量与单位", "主要读数", "生成命令"]
    else:
        return _reject("正文或表格能够更短地完成该职责，现有关系复杂度不足以支持新增图形", section, claim)

    return {
        "should_insert": True,
        "section": section,
        "claim": claim,
        "renderer": renderer,
        "figure_type": figure_type,
        "insertion_point": insertion,
        "required_inputs": required,
        "before_sentence_contract": "图前只提出该图要检验的对象、条件和读数，不提前评价结果",
        "after_paragraph_contract": "图后依次陈述观察、关键数值、形成原因及其对当前问题结论的影响",
        "style_family": "visio" if renderer == "paper-visio" else "tikz" if renderer == "paper-tikz" else "matlab",
        "formal_requirements": {
            "vector_output": True,
            "editable_source": True,
            "registry_entry": True,
            "final_page_review": True,
            "no_in_figure_caption": True,
        },
    }


@mcp.tool()
def health_check() -> str:
    """Report the available semantic routing families."""
    return json.dumps(
        {
            "ok": True,
            "renderers": ["paper-visio", "paper-tikz", "paper-matlab"],
            "forbidden_sections": sorted(FORBIDDEN_SECTIONS),
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def route_figure(spec: dict[str, Any]) -> str:
    """Decide whether to insert a figure and return renderer, type, placement and evidence contract."""
    return json.dumps(decide(spec), ensure_ascii=False, indent=2)


@mcp.tool()
def audit_figure_plan(plans: list[dict[str, Any]]) -> str:
    """Audit a paper-level figure plan for missing claims, duplicate duties and invalid renderers."""
    errors: list[str] = []
    claims: dict[str, int] = {}
    accepted = 0
    for index, plan in enumerate(plans):
        result = decide(plan)
        if result["should_insert"]:
            accepted += 1
            claim = result["claim"]
            claims[claim] = claims.get(claim, 0) + 1
            if result["renderer"] not in {"paper-visio", "paper-tikz", "paper-matlab"}:
                errors.append(f"plan[{index}] 使用未批准的绘图后端")
    for claim, count in claims.items():
        if count > 1:
            errors.append(f"同一证据命题重复规划 {count} 幅图: {claim}")
    return json.dumps(
        {"ok": not errors, "accepted": accepted, "rejected": len(plans) - accepted, "errors": errors},
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()
