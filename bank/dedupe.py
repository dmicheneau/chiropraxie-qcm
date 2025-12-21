"""
Déduplication des questions basée sur fingerprint et similarité textuelle.

Stratégie simple:
- Fingerprint = hash MD5 du prompt normalisé
- Similarité = ratio Levenshtein > 85%
- En cas de doublon: garder la première occurrence (ordre d'import = priorité)
- En cas de conflit de réponses: warning + garder première source
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any, Dict, List, Tuple


def normalize_text(text: str) -> str:
    """Normalise un texte pour comparaison (minuscules, sans accents, sans ponctuation)."""
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def compute_fingerprint(prompt: str) -> str:
    """Génère un fingerprint MD5 du prompt normalisé."""
    normalized = normalize_text(prompt)
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def levenshtein_ratio(s1: str, s2: str) -> float:
    """Calcule le ratio de similarité Levenshtein entre deux chaînes (0.0 à 1.0)."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    # Matrice de distances
    len1, len2 = len(s1), len(s2)
    if len1 > len2:
        s1, s2 = s2, s1
        len1, len2 = len2, len1

    current_row = list(range(len1 + 1))
    for i in range(1, len2 + 1):
        previous_row, current_row = current_row, [i] + [0] * len1
        for j in range(1, len1 + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if s1[j - 1] != s2[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    distance = current_row[len1]
    max_len = max(len1, len2)
    return 1.0 - (distance / max_len)


def are_questions_similar(q1: Dict[str, Any], q2: Dict[str, Any], threshold: float = 0.85) -> bool:
    """Vérifie si deux questions sont similaires (même prompt à ~85%)."""
    prompt1 = normalize_text(q1.get("prompt", ""))
    prompt2 = normalize_text(q2.get("prompt", ""))
    return levenshtein_ratio(prompt1, prompt2) >= threshold


def dedupe_questions_advanced(
    questions: List[Dict[str, Any]],
    similarity_threshold: float = 0.85,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Déduplique les questions en utilisant fingerprint + similarité.
    
    Returns:
        Tuple (questions_uniques, doublons_éliminés)
    """
    unique: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []
    
    # Index par fingerprint pour lookup rapide
    fingerprint_index: Dict[str, int] = {}
    # Liste des prompts normalisés pour comparaison de similarité
    normalized_prompts: List[str] = []

    for q in questions:
        prompt = q.get("prompt", "")
        fp = compute_fingerprint(prompt)
        norm_prompt = normalize_text(prompt)

        # 1. Vérifier fingerprint exact
        if fp in fingerprint_index:
            existing_idx = fingerprint_index[fp]
            existing_q = unique[existing_idx]
            _log_duplicate(q, existing_q, "fingerprint exact")
            duplicates.append(q)
            continue

        # 2. Vérifier similarité avec questions existantes
        found_similar = False
        for idx, existing_norm in enumerate(normalized_prompts):
            if levenshtein_ratio(norm_prompt, existing_norm) >= similarity_threshold:
                existing_q = unique[idx]
                _log_duplicate(q, existing_q, f"similarité ≥ {similarity_threshold:.0%}")
                duplicates.append(q)
                found_similar = True
                break

        if not found_similar:
            fingerprint_index[fp] = len(unique)
            normalized_prompts.append(norm_prompt)
            unique.append(q)

    return unique, duplicates


def _log_duplicate(new_q: Dict[str, Any], existing_q: Dict[str, Any], reason: str) -> None:
    """Log un doublon détecté (warning si réponses différentes)."""
    new_ans = new_q.get("answer", {}).get("answers", [])
    existing_ans = existing_q.get("answer", {}).get("answers", [])

    new_src = new_q.get("source", {}).get("ref", "?")
    existing_src = existing_q.get("source", {}).get("ref", "?")

    prompt_preview = (new_q.get("prompt", "")[:50] + "...") if len(new_q.get("prompt", "")) > 50 else new_q.get("prompt", "")

    if set(new_ans) != set(existing_ans):
        print(f"⚠️  CONFLIT: '{prompt_preview}' - réponses différentes!")
        print(f"   Source 1 ({existing_src}): {existing_ans} [GARDÉE]")
        print(f"   Source 2 ({new_src}): {new_ans} [IGNORÉE]")
    # else: silencieux pour doublons identiques


def merge_question_banks(
    *banks: List[Dict[str, Any]],
    similarity_threshold: float = 0.85,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fusionne plusieurs banques de questions avec déduplication.
    L'ordre des banques définit la priorité (première = plus haute).
    """
    all_questions: List[Dict[str, Any]] = []
    for bank in banks:
        all_questions.extend(bank)
    
    return dedupe_questions_advanced(all_questions, similarity_threshold)
