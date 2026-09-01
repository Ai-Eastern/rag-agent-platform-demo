"""Search persistent Chroma with query-stage visibility filtering."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.chroma_store import CHROMA_PATH, search


def main() -> int:
    parser = argparse.ArgumentParser(description="检索智达科技虚构知识库。")
    parser.add_argument("--query", required=True)
    parser.add_argument(
        "--visibility",
        required=True,
        action="append",
        help="允许的可见性，可重复传入：public、support、admin。",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--chroma-path", type=Path, default=CHROMA_PATH)
    args = parser.parse_args()
    try:
        results = search(args.query, args.visibility, args.top_k, args.chroma_path)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    payload = {
        "query": args.query.strip(),
        "allowed_visibilities": list(dict.fromkeys(args.visibility)),
        "results": [asdict(result) for result in results],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
