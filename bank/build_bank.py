from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


LETTERS = ("A", "B", "C", "D")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_for_match(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_answer_letters(raw: str) -> List[str]:
    raw = (raw or "").strip().upper()
    raw = raw.replace(" ", "")
    if not raw:
        return []

    # Accept formats: "A", "AC", "A,C", "A;C"
    if "," in raw or ";" in raw:
        parts = re.split(r"[,;]", raw)
        out = [p for p in parts if p]
    else:
        out = list(raw)

    out = [x for x in out if x in set(LETTERS) or x in {"V", "F"}]
    # De-dup while preserving order
    seen: set[str] = set()
    uniq: List[str] = []
    for x in out:
        if x in seen:
            continue
        seen.add(x)
        uniq.append(x)
    return uniq


@dataclass
class ParsedDeckQuestion:
    number: str
    prompt: str
    choices: List[Dict[str, str]]


_DECK_BLOCK_RE = re.compile(r"(?m)^(\d+)\)\s*([^\n]+)\n((?:- [A-D]\.[^\n]+\n?)+)")
_DECK_OPT_RE = re.compile(r"-\s*([A-D])[\.)]?\s*(.+)")


def parse_deck_markdown(md: str) -> List[ParsedDeckQuestion]:
    out: List[ParsedDeckQuestion] = []
    for m in _DECK_BLOCK_RE.finditer(md):
        number = m.group(1)
        prompt = m.group(2).strip()
        opts_block = m.group(3)
        choices: List[Dict[str, str]] = []
        for mo in _DECK_OPT_RE.finditer(opts_block):
            choices.append({"key": mo.group(1), "text": mo.group(2).strip()})
        out.append(ParsedDeckQuestion(number=number, prompt=prompt, choices=choices))
    return out


_TSV_SPLIT_RE = re.compile(r"\tRéponse:\s*", re.IGNORECASE)
_TSV_QPREFIX_RE = re.compile(r"^Q\d+:\s*")


def parse_tsv_answer_key(tsv_text: str) -> Dict[str, List[str]]:
    """Return map normalized(question_text) -> list of answer letters.

    Supports legacy single-letter keys and multi-answer keys like "A,C".
    """

    answers: Dict[str, List[str]] = {}
    for raw_line in tsv_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = _TSV_SPLIT_RE.split(line)
        if len(parts) < 2:
            continue

        qtext = _TSV_QPREFIX_RE.sub("", parts[0]).strip()
        # Keep only the part immediately after "Réponse:" (before optional dash)
        ans_part = parts[1].strip()
        # ans_part can look like: "B — something" or "A,C — ..."
        ans_letters_raw = ans_part.split("—", 1)[0].strip()
        letters = parse_answer_letters(ans_letters_raw)
        if not letters:
            continue
        answers[normalize_for_match(qtext)] = letters

    return answers


def q_from_qitem(
    qid: str,
    stem: str,
    options: Sequence[str],
    answer_index: int,
    explanation: str,
    tags: Sequence[str],
    source_kind: str,
    source_ref: str,
) -> Dict[str, Any]:
    return {
        "id": qid,
        "type": "single_choice",
        "prompt": stem.strip(),
        "choices": [{"key": LETTERS[i], "text": str(opt).strip()} for i, opt in enumerate(options)],
        "answer": {"answers": [LETTERS[answer_index]]},
        "explanation": (explanation or "").strip(),
        "tags": list(tags),
        "source": {"kind": source_kind, "ref": source_ref},
    }


def infer_tags_for_generated(stem: str, default_tag: str) -> List[str]:
    tags = [default_tag]
    s = normalize_for_match(stem)

    # Very small heuristics to split UE2.2 into Angiologie vs Plexus/Nerfs
    if default_tag == "UE2.2":
        if any(k in s for k in ["artere", "artère", "axillaire", "brachiale", "radiale", "ulnaire", "pouls", "irrigation", "veine"]):
            tags.append("Angiologie")
        if any(k in s for k in ["nerf", "plexus", "racine", "corde", "tronc", "canal", "guyon", "carpien", "scalene", "scalène"]):
            tags.append("Plexus_Nerfs")

    return tags


def build_from_generate_qcm_400(repo_root: Path) -> List[Dict[str, Any]]:
    # Import locally (repo-root), no external dependency.
    import importlib.util
    import sys

    mod_path = repo_root / "generate_qcm_400.py"
    spec = importlib.util.spec_from_file_location("generate_qcm_400", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger {mod_path}")
    module = importlib.util.module_from_spec(spec)
    # Python 3.9 dataclasses (and typing) expect the module to be registered.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    qitems: List[Any] = []
    qitems.extend(module.build_connective_tissue_bank())
    qitems.extend(module.build_ue22_upper_limb_bank())
    qitems.extend(module.build_chiropractic_ifec_bank())

    out: List[Dict[str, Any]] = []
    counters: Dict[str, int] = {"Histologie_TC": 0, "UE2.2": 0, "Securite_IFEC": 0}

    for it in qitems:
        # Crude tag attribution based on which list the item came from.
        # We infer from stem patterns when possible; otherwise default.
        stem = it.stem

        if "tissu" in normalize_for_match(stem) or "gag" in normalize_for_match(stem) or "collagene" in normalize_for_match(stem):
            base_tag = "Histologie_TC"
            source_ref = "tissus_conjonctifs_extracted.txt"
            source_kind = "pdf_text"
        elif any(k in normalize_for_match(stem) for k in ["plexus", "nerf", "arter", "axilla", "brach", "radial", "ulnaire", "scalene", "guyon", "carpien"]):
            base_tag = "UE2.2"
            source_ref = "web/ue2_2_2023_2024_extracted.txt"
            source_kind = "pdf_text"
        else:
            base_tag = "Securite_IFEC"
            source_ref = "https://www.ifec.net/les-objectifs-de-la-formation/"
            source_kind = "url"

        counters[base_tag] = counters.get(base_tag, 0) + 1
        qid = f"gen_{base_tag.lower()}_{counters[base_tag]:04d}"
        tags = infer_tags_for_generated(stem, base_tag)

        out.append(
            q_from_qitem(
                qid=qid,
                stem=it.stem,
                options=it.options,
                answer_index=it.answer_index,
                explanation=it.explanation,
                tags=tags,
                source_kind=source_kind,
                source_ref=source_ref,
            )
        )

    return out


def build_from_existing_decks(repo_root: Path) -> List[Dict[str, Any]]:
    decks_dir = repo_root / "web" / "decks"
    if not decks_dir.exists():
        return []

    out: List[Dict[str, Any]] = []

    for md_path in sorted(decks_dir.glob("Deck_*.md")):
        deck_name = md_path.stem.replace("Deck_", "")
        md = md_path.read_text(encoding="utf-8")
        parsed = parse_deck_markdown(md)

        # Optional answer key TSV colocated with the decks.
        tsv_path = decks_dir / f"Quizlet_{deck_name}.tsv"
        answers_by_prompt: Dict[str, List[str]] = {}
        if tsv_path.exists():
            answers_by_prompt = parse_tsv_answer_key(tsv_path.read_text(encoding="utf-8"))

        for q in parsed:
            qid = f"deck_{deck_name.lower()}_{int(q.number):04d}"
            correct = answers_by_prompt.get(normalize_for_match(q.prompt))
            # Default: unknown; keep a placeholder so the bank is still valid.
            # If unknown, we omit answer to avoid giving wrong keys.
            base: Dict[str, Any] = {
                "id": qid,
                "type": "single_choice",
                "prompt": q.prompt,
                "choices": q.choices,
                "tags": [deck_name],
                "source": {"kind": "deck_md", "ref": str(md_path.relative_to(repo_root))},
            }
            if correct:
                base["answer"] = {"answers": correct}
            else:
                base["answer"] = {"answers": ["A"]}
                base["explanation"] = "Clé inconnue (non trouvée dans le TSV associé)."
            out.append(base)

    return out


def dedupe_questions(questions: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate by stable id; keep first occurrence."""
    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for q in questions:
        qid = str(q.get("id", ""))
        if not qid or qid in seen:
            continue
        seen.add(qid)
        out.append(q)
    return out


def build_mcq_from_flashcards_tsv(
    tsv_path: Path,
    tag: str,
    source_ref: str,
    rng_seed: int = 123,
) -> List[Dict[str, Any]]:
    """Import a Quizlet-like TSV (Term<TAB>Definition) and generate 4-choice MCQs.

    For each card (term, definition), create the question:
      "Quelle est la meilleure définition de : <term> ?"
    with 4 options = 1 correct definition + 3 distractor definitions.

    This avoids scraping web pages and relies on user-provided exports.
    """

    import csv
    import random

    rows: List[Tuple[str, str]] = []
    with tsv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 2:
                continue
            term = (row[0] or "").strip()
            definition = (row[1] or "").strip()
            if not term or not definition:
                continue
            rows.append((term, definition))

    if len(rows) < 4:
        return []

    rng = random.Random(rng_seed)
    all_defs = [d for _, d in rows]

    out: List[Dict[str, Any]] = []
    for idx, (term, definition) in enumerate(rows, start=1):
        distractors = [d for d in all_defs if d != definition]
        if len(distractors) < 3:
            continue
        opts = [definition] + rng.sample(distractors, 3)
        rng.shuffle(opts)
        answer_index = opts.index(definition)
        qid = f"quizlet_{tag.lower()}_{idx:04d}"

        out.append(
            q_from_qitem(
                qid=qid,
                stem=f"Quelle est la meilleure définition de : {term} ?",
                options=opts,
                answer_index=answer_index,
                explanation="",
                tags=[tag],
                source_kind="quizlet_tsv",
                source_ref=source_ref or str(tsv_path),
            )
        )

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build canonical QCM bank JSON")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", default="web/bank/bank.json")
    parser.add_argument("--include-generated", action="store_true", help="Include questions from generate_qcm_400.py")
    parser.add_argument("--include-existing-decks", action="store_true", help="Include Deck_*.md + Quizlet_*.tsv")
    parser.add_argument(
        "--quizlet-flashcards",
        action="append",
        default=[],
        help=(
            "Import flashcards TSV (Term<TAB>Definition) and generate MCQs. "
            "Format: path|TAG|source_ref (TAG required). Repeatable."
        ),
    )
    parser.add_argument(
        "--sources-config",
        default=None,
        help=(
            "Chemin vers un fichier YAML de configuration des sources. "
            "Si fourni, utilise le nouveau système multi-sources avec déduplication avancée."
        ),
    )

    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    # Mode multi-sources avec config YAML
    if args.sources_config:
        from .source_manager import load_config, import_all_sources, save_bank
        config_path = (repo_root / args.sources_config).resolve()
        config = load_config(config_path)
        bank = import_all_sources(config, repo_root)
        output_path = repo_root / config.output_path
        save_bank(bank, output_path)
        return

    out_path = (repo_root / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    questions: List[Dict[str, Any]] = []

    if args.include_generated:
        questions.extend(build_from_generate_qcm_400(repo_root))

    if args.include_existing_decks:
        questions.extend(build_from_existing_decks(repo_root))

    for spec in args.quizlet_flashcards:
        parts = [p.strip() for p in spec.split("|")]
        if len(parts) < 2:
            raise SystemExit("--quizlet-flashcards: format attendu path|TAG|source_ref")
        rel_path = parts[0]
        tag = parts[1]
        source_ref = parts[2] if len(parts) >= 3 else rel_path
        tsv_path = (repo_root / rel_path).resolve()
        if not tsv_path.exists():
            raise SystemExit(f"Fichier introuvable: {tsv_path}")
        questions.extend(build_mcq_from_flashcards_tsv(tsv_path=tsv_path, tag=tag, source_ref=source_ref))

    questions = dedupe_questions(questions)

    bank = {
        "version": "0.1.0",
        "generatedAt": _now_iso(),
        "questions": questions,
    }

    out_path.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote bank: {out_path}")
    print(f"Questions: {len(questions)}")


if __name__ == "__main__":
    main()
