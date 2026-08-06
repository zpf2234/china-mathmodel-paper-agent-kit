from __future__ import annotations

import importlib.util
from pathlib import Path


SKILLS = Path(__file__).resolve().parents[2]
SCRIPT = SKILLS / "cumcm-review/scripts/audit_artifacts.py"
SYNC_SCRIPT = SKILLS / "cumcm-review/scripts/sync_review_artifacts.py"
spec = importlib.util.spec_from_file_location("audit_artifacts_under_test", SCRIPT)
assert spec and spec.loader
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


def load_module(name: str, path: Path):
    module_spec = importlib.util.spec_from_file_location(name, path)
    assert module_spec and module_spec.loader
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


SYNC = load_module("sync_review_artifacts_under_test", SYNC_SCRIPT)


def test_sync_censuses_figures_from_modular_tex(tmp_path: Path):
    main = tmp_path / "论文.tex"
    child = tmp_path / "章节.tex"
    main.write_text(r"\graphicspath{{figures/}}\input{章节.tex}", encoding="utf-8")
    child.write_text(
        r"\begin{figure}\includegraphics[width=.8\textwidth]{curve.pdf}\caption{结果曲线}\label{fig:curve}\end{figure}",
        encoding="utf-8",
    )
    figures = SYNC.tex_figure_environments(main)
    assert len(figures) == 1
    assert figures[0]["label"] == "fig:curve"
    assert figures[0]["source_tex"] == child.resolve()


def test_pdf_reference_heading_fallback_finds_real_heading_not_inline_mention():
    pages = [
        "摘要 关键词",
        "正文中引用参考文献[1]说明方法来源。",
        "七、结论",
        "参考文献\n[1] Wald A. Sequential Analysis.",
        "附录 A 程序说明",
    ]
    assert AUDIT.detect_references_start_page(pages) == 4


def test_pdf_reference_fallback_rejects_bibliography_word_without_entries():
    pages = ["摘要", "本文参考文献中的方法用于比较。", "结论"]
    assert AUDIT.detect_references_start_page(pages) is None


def test_single_file_abstract_is_used_without_zero_abstract_module(tmp_path: Path):
    main = tmp_path / "论文.tex"
    main.write_text(
        r"\begin{document}\begin{abstract}定量结果为 1.2。\keywords{模型；验证}\end{abstract}\end{document}",
        encoding="utf-8",
    )
    source_path, abstract_text = AUDIT.resolve_abstract_source(main, [main])
    assert source_path == main
    assert "定量结果为 1.2" in abstract_text


def test_no_appendix_is_legal_when_source_has_no_appendix_marker():
    hard, warnings = AUDIT.audit_appendix(Path("论文"), r"\section{结论}正文结束。", [])
    assert hard == []
    assert any("no appendix" in warning for warning in warnings)


def test_inline_appendix_is_audited_as_appendix_content(tmp_path: Path):
    source = r"""
    \section{结论}正文。
    \appendix
    \section{复现说明}\label{app:reproduce}
    支撑材料清单。运行环境：Python 3.11。
    \begin{lstlisting}print(1)\end{lstlisting}
    """
    hard, _ = AUDIT.audit_appendix(tmp_path, source, [])
    assert hard == []


def test_formula_colon_and_terminal_punctuation_are_contextual_warnings():
    tex = r"由定义可得\begin{equation}x=1.\end{equation}"
    hard, warnings = AUDIT.audit_formula_style(tex)
    assert hard == []
    assert any("not introduced by a colon" in item for item in warnings)
    assert any("ends with punctuation" in item for item in warnings)


def test_parallel_aligned_derivation_does_not_require_left_brace():
    tex = r"推导如下：\begin{align}a&=b+c\\d&=e+f\end{align}"
    hard, warnings = AUDIT.audit_formula_style(tex)
    assert not any("lacks a left brace" in item for item in hard)
    assert not any("lacks a left brace" in item for item in warnings)


def test_true_equation_system_without_left_brace_remains_hard_error():
    tex = r"联立方程组：\begin{equation}\begin{aligned}x&=1\\y&=2\end{aligned}\end{equation}"
    hard, _ = AUDIT.audit_formula_style(tex)
    assert any("true equation system" in item and "lacks a left brace" in item for item in hard)


def test_contest_year_configuration_controls_ai_and_limits():
    rules_2024 = AUDIT.contest_rules(2024)
    rules_2026 = AUDIT.contest_rules(2026)
    assert rules_2024["body_page_limit"] == 30
    assert rules_2024["size_limit_mb"] == 20.0
    assert rules_2024["ai_disclosure_required"] is False
    assert rules_2026["ai_disclosure_required"] is True


def test_language_audit_excludes_inline_appendix():
    language = load_module(
        "language_audit_under_test", SKILLS / "cumcm-language-audit/scripts/audit_language.py"
    )
    with __import__("tempfile").TemporaryDirectory() as tmp:
        path = Path(tmp) / "论文.tex"
        path.write_text(r"正文结论。\appendix\section{代码}完整程序见附录。", encoding="utf-8")
        assert language.scan(path, language.HARD_PATTERNS) == []


def test_section_chain_treats_absent_appendix_stage_as_optional():
    section_chain = load_module(
        "section_chain_under_test", SKILLS / "cumcm-paper/scripts/audit_section_chain.py"
    )
    assert "appendix" not in section_chain.REQUIRED_STAGES
    assert "appendix" in section_chain.OPTIONAL_STAGES


def test_scientific_gate_patterns_are_not_weakened():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "求解/证据矩阵.csv missing" in source
    assert "solve-stage evidence audit failed" in source
    assert "scorecard dimension lacks evidence" in source
    assert "provenance input SHA-256 mismatch or missing" in source
