from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_bank(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def has_tag(q: Dict[str, Any], tag: str) -> bool:
    tags = q.get("tags") or []
    return tag in tags


def filter_questions(questions: Sequence[Dict[str, Any]], include_tags: Sequence[str]) -> List[Dict[str, Any]]:
    if not include_tags:
        return list(questions)

    out: List[Dict[str, Any]] = []
    for q in questions:
        if any(has_tag(q, t) for t in include_tags):
            out.append(q)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a quiz JSON (random subset) from the bank")
    parser.add_argument("--bank", default="web/bank/bank.json")
    parser.add_argument("--out", default="web/bank/quiz.json")
    parser.add_argument("--tag", action="append", default=[], help="Filter by tag (repeatable)")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed", type=int, default=None)

    args = parser.parse_args()

    bank_path = Path(args.bank).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bank = load_bank(bank_path)
    questions = bank.get("questions") or []
    selected_pool = filter_questions(questions, args.tag)

    if args.count <= 0:
        raise SystemExit("--count doit être > 0")

    if not selected_pool:
        raise SystemExit("Aucune question ne correspond aux tags demandés")

    rng = random.Random(args.seed)
    if args.count >= len(selected_pool):
        picked = list(selected_pool)
        rng.shuffle(picked)
    else:
        picked = rng.sample(list(selected_pool), args.count)

    quiz = {
        "version": "0.1.0",
        "generatedAt": _now_iso(),
        "seed": args.seed,
        "tags": args.tag,
        "questions": picked,
    }

    out_path.write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote quiz: {out_path}")
    print(f"Questions: {len(picked)}")


if __name__ == "__main__":
    main()
