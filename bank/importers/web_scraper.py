"""
Web scraper pour extraire des flashcards et QCM depuis le web.

Sources supportées:
- Quizlet (flashcards)
- Autres sites de QCM (à étendre)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


@dataclass
class Flashcard:
    """Une flashcard extraite."""
    term: str
    definition: str


def parse_quizlet_html(html_content: str) -> List[Flashcard]:
    """
    Parse le contenu HTML de Quizlet pour extraire les flashcards.
    
    Fonctionne avec le HTML récupéré via fetch ou scraping.
    """
    flashcards: List[Flashcard] = []
    
    # Pattern pour extraire les paires terme/définition
    # Format Quizlet typique: data contenue dans des divs avec classes spécifiques
    
    # Méthode 1: Chercher les patterns JSON embarqués
    json_pattern = re.compile(r'"word"\s*:\s*"([^"]+)"\s*,\s*"definition"\s*:\s*"([^"]+)"')
    for match in json_pattern.finditer(html_content):
        term = _unescape_json_string(match.group(1))
        definition = _unescape_json_string(match.group(2))
        if term and definition:
            flashcards.append(Flashcard(term=term, definition=definition))
    
    # Si méthode 1 échoue, essayer méthode 2: patterns HTML
    if not flashcards:
        # Pattern pour divs de cartes
        term_pattern = re.compile(r'class="[^"]*(?:SetPageTerm|TermText)[^"]*"[^>]*>([^<]+)<', re.IGNORECASE)
        def_pattern = re.compile(r'class="[^"]*(?:SetPageDefinition|DefinitionText)[^"]*"[^>]*>([^<]+)<', re.IGNORECASE)
        
        terms = [_clean_html_text(m.group(1)) for m in term_pattern.finditer(html_content)]
        defs = [_clean_html_text(m.group(1)) for m in def_pattern.finditer(html_content)]
        
        for term, definition in zip(terms, defs):
            if term and definition:
                flashcards.append(Flashcard(term=term, definition=definition))
    
    return flashcards


def _unescape_json_string(s: str) -> str:
    """Décode les échappements JSON."""
    return (s
        .replace("\\n", "\n")
        .replace("\\r", "")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
        .encode().decode("unicode_escape", errors="ignore")
    )


def _clean_html_text(text: str) -> str:
    """Nettoie le texte HTML."""
    # Décoder les entités HTML
    import html
    text = html.unescape(text)
    # Supprimer les espaces multiples
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def flashcards_to_bank_questions(
    flashcards: List[Flashcard],
    source_ref: str,
    tags: Optional[List[str]] = None,
    id_prefix: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Convertit des flashcards en questions au format banque.
    
    Les flashcards deviennent des questions de type "flashcard" (terme/définition).
    """
    questions: List[Dict[str, Any]] = []
    prefix = id_prefix or source_ref.replace("/", "_").replace("-", "_")
    
    for idx, card in enumerate(flashcards, 1):
        q_id = f"{prefix}_{idx:04d}"
        
        q: Dict[str, Any] = {
            "id": q_id,
            "type": "flashcard",
            "prompt": card.term,
            "options": {},  # Pas d'options pour flashcard
            "answer": {
                "text": card.definition,
                "answers": [],
            },
            "tags": tags or [],
            "source": {
                "ref": source_ref,
                "date": None,
            },
        }
        questions.append(q)
    
    return questions


def load_tsv_flashcards(tsv_path: str | Path) -> List[Flashcard]:
    """Charge des flashcards depuis un fichier TSV (Term\\tDefinition)."""
    flashcards: List[Flashcard] = []
    path = Path(tsv_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Fichier TSV non trouvé: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            parts = line.split("\t")
            if len(parts) >= 2:
                term = parts[0].replace("\\n", "\n").strip()
                definition = parts[1].replace("\\n", "\n").strip()
                flashcards.append(Flashcard(term=term, definition=definition))
            else:
                print(f"⚠️  Ligne {line_num} ignorée (pas de tabulation): {line[:50]}...")
    
    return flashcards


def import_tsv(
    tsv_path: str | Path,
    source_ref: str,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Importe un fichier TSV de flashcards et retourne des questions au format banque.
    """
    flashcards = load_tsv_flashcards(tsv_path)
    return flashcards_to_bank_questions(flashcards, source_ref, tags)


def detect_source_type(url_or_path: str) -> str:
    """Détecte le type de source (quizlet, tsv, pdf, unknown)."""
    lower = url_or_path.lower()
    
    if "quizlet.com" in lower:
        return "quizlet"
    elif lower.endswith(".tsv"):
        return "tsv"
    elif lower.endswith(".pdf"):
        return "pdf"
    elif lower.endswith(".md"):
        return "markdown"
    else:
        return "unknown"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python web_scraper.py <fichier.tsv>")
        sys.exit(1)
    
    tsv_file = sys.argv[1]
    try:
        flashcards = load_tsv_flashcards(tsv_file)
        print(f"Chargé {len(flashcards)} flashcards depuis {tsv_file}")
        for fc in flashcards[:3]:
            print(f"\n  Terme: {fc.term[:50]}...")
            print(f"  Déf:   {fc.definition[:50]}...")
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)
