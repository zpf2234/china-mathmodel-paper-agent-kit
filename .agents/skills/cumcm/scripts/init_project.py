#!/usr/bin/env python
"""Initialize the standard CUMCM workspace layout."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


DIRS = ["题目", "数据", "求解", "论文", "审查"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="CUMCM project root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    for name in DIRS:
        (root / name).mkdir(exist_ok=True)

    state = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "layout": DIRS,
        "contract": "CUMCM 2026 electronic paper: abstract first page, no table of contents, paper <=20MB, support archive <=20MB.",
        "page_policy": {
            "body_definition": "abstract first page through the page before references:start",
            "body_page_min": 20,
            "body_page_max": 30,
            "references_start_on_new_page": True,
            "appendix_and_after_page_limit": None,
        },
    }
    state_path = root / ".cumcm_state.json"
    if not state_path.exists():
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Initialized CUMCM workspace: {root}")
    for name in DIRS:
        print(f"- {name}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
