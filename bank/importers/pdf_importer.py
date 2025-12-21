"""
Importeur de QCM depuis des fichiers PDF.

Utilise PyMuPDF (fitz) pour extraire le texte.
Détecte automatiquement les formats de QCM courants.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # type: ignore


@dataclass
class ExtractedQuestion:
    """Question extraite d'un PDF."""
    number: int
    prompt: str
    choices: List[str]  # ["A. ...", "B. ...", ...]
    correct_answers: Optional[List[str]] = None  # ["A", "B", ...] si correction incluse


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extrait le texte brut d'un fichier PDF."""
    if fitz is None:
        raise ImportError(
            "PyMuPDF non installé. Installez-le avec: pip install pymupdf"
        )
    
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier PDF non trouvé: {path}")

    doc = fitz.open(str(path))
    text_parts: List[str] = []
    
    for page in doc:
        text_parts.append(page.get_text())
    
    doc.close()
    return "\n".join(text_parts)


# Patterns pour détecter les questions
_QUESTION_PATTERNS = [
    # Format: "1. Question text" ou "1) Question text"
    re.compile(r"^(\d+)[.\)]\s*(.+?)(?=\n[A-E][.\)]|\Z)", re.MULTILINE | re.DOTALL),
    # Format: "Question 1:" ou "Q1:"
    re.compile(r"^(?:Question\s*|Q)(\d+)\s*:\s*(.+?)(?=\n[A-E][.\)]|\Z)", re.MULTILINE | re.DOTALL | re.IGNORECASE),
]

# Patterns pour détecter les choix
_CHOICE_PATTERN = re.compile(r"^([A-E])[.\)]\s*(.+?)(?=\n[A-E][.\)]|\n\d+[.\)]|\n(?:Question|Q)\d+|\Z)", re.MULTILINE | re.DOTALL)

# Patterns pour détecter les réponses correctes
_ANSWER_PATTERNS = [
    # Format: "Réponse: A" ou "Réponses: A, B, C"
    re.compile(r"R[ée]ponses?\s*:\s*([A-E](?:\s*,\s*[A-E])*)", re.IGNORECASE),
    # Format: "Corrigé: A" ou "Correction: A, B"
    re.compile(r"(?:Corrig[ée]|Correction)\s*:\s*([A-E](?:\s*,\s*[A-E])*)", re.IGNORECASE),
    # Format simple: juste les lettres entre crochets [A, B]
    re.compile(r"\[([A-E](?:\s*,\s*[A-E])*)\]"),
]


def parse_qcm_from_text(text: str) -> List[ExtractedQuestion]:
    """Parse le texte extrait pour trouver les QCM."""
    questions: List[ExtractedQuestion] = []
    
    # Essayer chaque pattern de question
    for pattern in _QUESTION_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            for match in matches:
                q_num = int(match.group(1))
                q_text = match.group(2).strip()
                
                # Chercher les choix après cette question
                start_pos = match.end()
                # Trouver où commence la prochaine question
                next_q = pattern.search(text, start_pos)
                end_pos = next_q.start() if next_q else len(text)
                
                choices_section = text[match.start():end_pos]
                choices = _extract_choices(choices_section)
                
                if choices:
                    # Chercher les réponses correctes
                    answers = _extract_answers(choices_section)
                    
                    questions.append(ExtractedQuestion(
                        number=q_num,
                        prompt=q_text,
                        choices=choices,
                        correct_answers=answers,
                    ))
            break  # Un pattern a matché, pas besoin d'essayer les autres
    
    return questions


def _extract_choices(text: str) -> List[str]:
    """Extrait les choix de réponse d'un bloc de texte."""
    choices: List[str] = []
    for match in _CHOICE_PATTERN.finditer(text):
        letter = match.group(1).upper()
        choice_text = match.group(2).strip()
        choices.append(f"{letter}. {choice_text}")
    return choices


def _extract_answers(text: str) -> Optional[List[str]]:
    """Extrait les réponses correctes si présentes."""
    for pattern in _ANSWER_PATTERNS:
        match = pattern.search(text)
        if match:
            answers_str = match.group(1)
            return [a.strip().upper() for a in answers_str.split(",")]
    return None


def import_pdf(
    pdf_path: str | Path,
    source_ref: str,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Importe un PDF et retourne des questions au format banque.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        source_ref: Référence de la source (ex: "IFEC_2023_UE2")
        tags: Tags à appliquer aux questions
    
    Returns:
        Liste de questions au format JSON banque
    """
    text = extract_text_from_pdf(pdf_path)
    extracted = parse_qcm_from_text(text)
    
    questions: List[Dict[str, Any]] = []
    for eq in extracted:
        q_id = f"{source_ref}_Q{eq.number:03d}"
        
        # Construire les options
        options = {}
        for choice in eq.choices:
            letter = choice[0]
            text = choice[3:].strip()  # Enlever "A. "
            options[letter] = text
        
        q: Dict[str, Any] = {
            "id": q_id,
            "type": "mcq",
            "prompt": eq.prompt,
            "options": options,
            "answer": {
                "answers": eq.correct_answers or [],
            },
            "tags": tags or [],
            "source": {
                "ref": source_ref,
                "date": None,
            },
        }
        questions.append(q)
    
    return questions


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_importer.py <fichier.pdf>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    try:
        text = extract_text_from_pdf(pdf_file)
        questions = parse_qcm_from_text(text)
        print(f"Trouvé {len(questions)} questions dans {pdf_file}")
        for q in questions[:3]:
            print(f"\n{q.number}. {q.prompt[:50]}...")
            for c in q.choices:
                print(f"   {c[:40]}...")
            if q.correct_answers:
                print(f"   Réponse(s): {', '.join(q.correct_answers)}")
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)
