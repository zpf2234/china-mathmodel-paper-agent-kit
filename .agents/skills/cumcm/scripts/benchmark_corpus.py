#!/usr/bin/env python
"""Profile local excellent-paper PDFs and audit first-page similarity."""

from __future__ import annotations

import argparse
import fnmatch
import json
import logging
import re
import statistics
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.ERROR)


def load_reader():
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        from PyPDF2 import PdfReader  # type: ignore
    return PdfReader


def normalize(text: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", text.lower())


def ngrams(text: str, width: int) -> set[str]:
    if len(text) < width:
        return {text} if text else set()
    return {text[i : i + width] for i in range(len(text) - width + 1)}


def containment(candidate: str, reference: str, width: int = 8) -> float:
    candidate_grams = ngrams(normalize(candidate), width)
    if not candidate_grams:
        return 0.0
    return len(candidate_grams & ngrams(normalize(reference), width)) / len(candidate_grams)


def extract_abstract(first_page: str) -> str:
    start = re.search(r"摘\s*要", first_page)
    if not start:
        return ""
    body = first_page[start.end() :]
    end = re.search(r"关\s*键\s*词", body)
    return body[: end.start()] if end else body


def quantile(values: list[int], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return float(ordered[index])


def infer_track(root: Path) -> str | None:
    problem_dir = root / "题目"
    names = " ".join(path.name.upper() for path in problem_dir.glob("*"))
    has_a = bool(re.search(r"(^|[^A-Z])A\s*题", names))
    has_b = bool(re.search(r"(^|[^A-Z])B\s*题", names))
    if has_a and not has_b:
        return "A"
    if has_b and not has_a:
        return "B"
    return None


def title_tokens(text: str) -> set[str]:
    compact = normalize(text)
    for phrase in (
        "基于",
        "模型",
        "优化",
        "设计",
        "研究",
        "问题",
        "目标",
        "动态",
        "方法",
        "分析",
        "形态",
        "形状",
        "调节",
    ):
        compact = compact.replace(phrase, "")
    return ngrams(compact, 2)


def title_similarity(left: str, right: str) -> float:
    left_tokens = title_tokens(left)
    right_tokens = title_tokens(right)
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 0.0


def title_from_filename(name: str) -> str:
    stem = Path(name).stem
    return re.sub(r"^[\(（][AB]\d+[\)）]", "", stem, flags=re.IGNORECASE)


def load_corpus_map(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"invalid corpus map {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"corpus map root must be an object: {path}")
    return {
        str(title): [str(pattern) for pattern in patterns]
        for title, patterns in value.items()
        if isinstance(patterns, list)
    }


def mapped_priority(problem_title: str, filename: str, corpus_map: dict[str, list[str]]) -> int:
    normalized_problem = normalize(problem_title)
    for mapped_title, patterns in corpus_map.items():
        normalized_mapped = normalize(mapped_title)
        if normalized_problem not in normalized_mapped and normalized_mapped not in normalized_problem:
            continue
        if any(fnmatch.fnmatch(filename, pattern) for pattern in patterns):
            return 1
    return 0


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line and not re.fullmatch(r"\d+", line):
            return line
    return ""


def problem_title_from_text(text: str) -> str:
    match = re.search(r"(?:^|\n)\s*[AB]\s*题\s+([^\n]{2,80})", text, flags=re.IGNORECASE)
    if not match:
        return ""
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return re.split(r"(?:请建立|问题\s*1|现计划)", title, maxsplit=1)[0].strip()


def discover_problem(root: Path, explicit: str | None) -> tuple[Path | None, str]:
    candidates = [Path(explicit)] if explicit else sorted((root / "题目").glob("*.pdf"))
    for candidate in candidates:
        path = candidate if candidate.is_absolute() else (root / candidate)
        if not path.exists():
            continue
        try:
            item = extract_pdf(path)
        except Exception:  # noqa: BLE001
            continue
        title = problem_title_from_text(item["first_page"])
        if title:
            return path.resolve(), title
        return path.resolve(), path.stem
    return None, ""


def track_from_problem(path: Path | None) -> str | None:
    if path is None:
        return None
    match = re.search(r"([AB])\s*题", path.name.upper())
    if match:
        return match.group(1)
    try:
        text = extract_pdf(path)["first_page"]
    except Exception:  # noqa: BLE001
        return None
    match = re.search(r"(?:^|\n)\s*([AB])\s*题", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


def extract_pdf(path: Path, full_text: bool = False) -> dict:
    PdfReader = load_reader()
    reader = PdfReader(str(path))
    first_page = reader.pages[0].extract_text() or "" if reader.pages else ""
    result = {
        "path": str(path),
        "name": path.name,
        "pages": len(reader.pages),
        "title": first_nonempty_line(first_page),
        "first_page": first_page,
    }
    if full_text:
        pages = [(page.extract_text() or "") for page in reader.pages]
        text = "\n".join(pages)
        figure_ids = set(re.findall(r"图\s*\d+(?:[.\-]\d+)?", text))
        table_ids = set(re.findall(r"表\s*\d+(?:[.\-]\d+)?", text))
        extraction_quality = (
            "low"
            if len(normalize(text)) < 1000
            or (len(reader.pages) > 10 and not figure_ids and not table_ids)
            else "ok"
        )
        appendix_page = None
        for index, page_text in enumerate(pages, start=1):
            if index > len(pages) // 2 and re.search(r"(^|\n)\s*附\s*录\s*($|\n)", page_text):
                appendix_page = index
                break
        result.update(
            {
                "_full_text": text,
                "figures_approx": len(figure_ids),
                "tables_approx": len(table_ids),
                "extraction_quality": extraction_quality,
                "appendix_start_approx": appendix_page,
                "validation_signals": {
                    key: key in text
                    for key in ["误差分析", "灵敏度", "稳健性", "残差", "收敛", "约束满足"]
                },
            }
        )
    return result


def corpus_stats(items: list[dict]) -> dict:
    pages = [int(item["pages"]) for item in items]
    return {
        "count": len(pages),
        "pages": {
            "min": min(pages) if pages else None,
            "q25": quantile(pages, 0.25),
            "median": statistics.median(pages) if pages else None,
            "q75": quantile(pages, 0.75),
            "max": max(pages) if pages else None,
        },
    }


def write_report(output_dir: Path, result: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "优秀论文对标.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    stats = result["corpus_stats"]["pages"]
    lines = [
        "# 优秀论文语料对标",
        "",
        f"- 语料数量：{result['corpus_stats']['count']}",
        f"- 赛道：{result['track'] or '未判定'}",
        f"- 赛题：{result['problem_title'] or '未提取'}",
        f"- 页数分布：{stats['min']} / {stats['q25']} / {stats['median']} / "
        f"{stats['q75']} / {stats['max']}（最小/Q1/中位数/Q3/最大）",
        "",
        "## 邻近样本",
    ]
    if not result["peers"]:
        lines.append("- 未找到可靠的同题或近题语料；本轮只使用赛道级页数统计。")
    for item in result["peers"]:
        signals = "、".join(key for key, value in item["validation_signals"].items() if value) or "未检出"
        if item["extraction_quality"] == "low":
            lines.append(
                f"- {item['name']}：{item['pages']} 页，PDF 文本层异常，"
                "图表与验证统计需 OCR/人工复核"
            )
        else:
            lines.append(
                f"- {item['name']}：{item['pages']} 页，图约 {item['figures_approx']}，"
                f"表约 {item['tables_approx']}，验证信号：{signals}"
            )
    lines.extend(["", "## 原创性预警"])
    similarity = result["similarity"]
    if similarity["available"]:
        if similarity.get("corpus_extraction_limited"):
            lines.append("- 同题样本文本层不可提取，未获得可解释的摘要或全文 containment；需 OCR/人工复核。")
        else:
            lines.append(
                f"- 最高摘要 containment：{similarity['max_containment']:.3f}"
                f"（{similarity['closest_paper']}）"
            )
        if similarity["full_text_containment"] is not None:
            lines.append(
                f"- 对最高风险论文的全文 containment："
                f"{similarity['full_text_containment']:.3f}"
            )
        lines.append(f"- 结论：{similarity['status']}")
        manual_review = result.get("manual_review")
        if isinstance(manual_review, dict):
            lines.append(f"- 独立人工复核：{'PASS' if manual_review.get('pass') else 'FAIL'}")
    else:
        lines.append("- 候选论文尚未生成，未执行相似度审计。")
    lines.extend(
        [
            "",
            "> 页数与图表数仅用于校准，不是写作配额；官方格式、题目需要和证据完整性优先。",
        ]
    )
    (output_dir / "优秀论文对标.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="CUMCM project root")
    parser.add_argument("--corpus", default="最终效果/高教杯优秀论文")
    parser.add_argument("--paper", default="论文/论文.pdf")
    parser.add_argument("--problem", help="problem PDF; defaults to 题目/*.pdf")
    parser.add_argument("--corpus-map", help="JSON mapping problem titles to corpus filename globs")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--fail-on-similarity", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    corpus_dir = (root / args.corpus).resolve()
    paper_path = (root / args.paper).resolve()
    map_path = (
        Path(args.corpus_map).resolve()
        if args.corpus_map
        else Path(__file__).resolve().parent.parent / "references" / "corpus-map.json"
    )
    corpus_map = load_corpus_map(map_path)
    if not corpus_dir.exists():
        raise SystemExit(f"benchmark corpus missing: {corpus_dir}")

    problem_path, problem_title = discover_problem(root, args.problem)
    track = track_from_problem(problem_path) or infer_track(root)
    metadata: list[dict] = []
    for path in sorted(corpus_dir.glob("*.pdf")):
        try:
            item = extract_pdf(path)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: skipped {path.name}: {exc}")
            continue
        match = re.search(r"[\(（]([AB])\d+", path.name.upper())
        if match is None:
            match = re.search(r"([AB])\s*题", path.name.upper())
        item["track"] = match.group(1) if match else None
        metadata.append(item)

    eligible = [item for item in metadata if not track or item["track"] in {track, None}]
    candidate_title = ""
    candidate_first_page = ""
    candidate_abstract = ""
    if paper_path.exists():
        candidate = extract_pdf(paper_path)
        candidate_title = candidate["title"]
        candidate_first_page = candidate["first_page"]
        candidate_abstract = extract_abstract(candidate_first_page)

    ranking_title = problem_title or candidate_title
    scored = [
        (
            mapped_priority(problem_title, item["name"], corpus_map),
            title_similarity(ranking_title, title_from_filename(item["name"])),
            item,
        )
        for item in eligible
    ]
    ranked = [
        item
        for mapped, similarity_score, item in sorted(scored, key=lambda row: (row[0], row[1]), reverse=True)
        if mapped or similarity_score > 0
    ]
    selected_metadata = ranked[: max(1, args.top_k)]
    peers = []
    for item in selected_metadata:
        try:
            peer = extract_pdf(Path(item["path"]), full_text=True)
            peer.pop("first_page", None)
            peer.pop("_full_text", None)
            peers.append(peer)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: peer profiling failed for {item['name']}: {exc}")

    similarity = {
        "available": bool(candidate_first_page),
        "max_containment": 0.0,
        "closest_paper": None,
        "full_text_containment": None,
        "scope": "selected same/near-problem peers",
        "corpus_extraction_limited": False,
        "status": "NOT_RUN",
    }
    if candidate_abstract:
        scored = [
            (
                containment(candidate_abstract, extract_abstract(item["first_page"])),
                item["name"],
                item["path"],
            )
            for item in selected_metadata
            if extract_abstract(item["first_page"])
        ]
        best_score, best_name, best_path = max(scored, default=(0.0, None, None))
        full_score = None
        if best_path and best_score >= 0.15:
            candidate_full = extract_pdf(paper_path, full_text=True)["_full_text"]
            reference_full = extract_pdf(Path(best_path), full_text=True)["_full_text"]
            full_score = containment(candidate_full, reference_full, width=12)
        failed = best_score >= 0.30 or (full_score is not None and full_score >= 0.20)
        warned = best_score >= 0.15 or (full_score is not None and full_score >= 0.10)
        extraction_limited = bool(peers) and all(
            item.get("extraction_quality") == "low" for item in peers
        )
        status = "FAIL_HIGH_SIMILARITY" if failed else "WARN_REVIEW" if warned else "PASS"
        if extraction_limited or not scored:
            status = "WARN_REVIEW" if not failed else status
        similarity.update(
            {
                "max_containment": best_score,
                "closest_paper": best_name,
                "full_text_containment": full_score,
                "corpus_extraction_limited": extraction_limited or not scored,
                "status": status,
            }
        )

    result = {
        "track": track,
        "problem_path": str(problem_path) if problem_path else None,
        "problem_title": problem_title,
        "corpus_map": str(map_path),
        "candidate_title": candidate_title,
        "corpus_stats": corpus_stats(eligible),
        "peers": peers,
        "similarity": similarity,
    }
    if args.no_write:
        print(
            json.dumps(
                {
                    "track": track,
                    "problem_title": problem_title,
                    "corpus_stats": result["corpus_stats"],
                    "peers": [item["name"] for item in peers],
                    "similarity": similarity,
                },
                ensure_ascii=False,
            )
        )
    else:
        write_report(root / "审查", result)
        print(f"Wrote {root / '审查' / '优秀论文对标.md'}")
    if args.fail_on_similarity and similarity["status"] == "FAIL_HIGH_SIMILARITY":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
