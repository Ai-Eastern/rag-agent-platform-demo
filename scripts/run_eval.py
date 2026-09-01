"""Run the frozen T2Retrieval subset evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROJECT_ROOT  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "运行 T2Retrieval 60×3000 检索子集（仅 retrieval）。"
            "结果为非官方完整成绩，不代表权限/工具评测或政企 RAG 质量。"
        )
    )
    parser.add_argument("--top-k", type=int, choices=(5,), default=5)
    args = parser.parse_args()
    try:
        from src.eval.retrieval_eval import run_evaluation

        report = run_evaluation(top_k=args.top_k)
    except Exception:
        print(json.dumps({"status": "error", "error": "评测运行失败。"}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
