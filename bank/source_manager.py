"""
Gestionnaire de sources pour l'import multi-sources.

Lit une configuration YAML et orchestre l'import de toutes les sources
avec déduplication automatique.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from .dedupe import dedupe_questions_advanced, merge_question_banks
from .importers import import_pdf, import_tsv, detect_source_type


@dataclass
class SourceConfig:
    """Configuration d'une source."""
    name: str
    type: str  # "tsv", "pdf", "markdown", "quizlet"
    path: str  # Chemin relatif ou URL
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0  # Plus petit = plus prioritaire


@dataclass
class BankConfig:
    """Configuration complète de la banque."""
    sources: List[SourceConfig]
    output_path: str = "web/bank/bank.json"
    similarity_threshold: float = 0.85


def load_config(config_path: str | Path) -> BankConfig:
    """Charge la configuration depuis un fichier YAML."""
    if yaml is None:
        raise ImportError("PyYAML non installé. Installez-le avec: pip install pyyaml")
    
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    sources = []
    for idx, src in enumerate(data.get("sources", [])):
        sources.append(SourceConfig(
            name=src.get("name", f"source_{idx}"),
            type=src.get("type", "auto"),
            path=src.get("path", ""),
            tags=src.get("tags", []),
            enabled=src.get("enabled", True),
            priority=src.get("priority", idx),
        ))
    
    # Trier par priorité
    sources.sort(key=lambda s: s.priority)
    
    return BankConfig(
        sources=sources,
        output_path=data.get("output", "web/bank/bank.json"),
        similarity_threshold=data.get("similarity_threshold", 0.85),
    )


def import_source(source: SourceConfig, base_path: Path) -> List[Dict[str, Any]]:
    """Importe une source et retourne les questions."""
    if not source.enabled:
        print(f"⏭️  Source désactivée: {source.name}")
        return []
    
    # Résoudre le chemin
    src_path = base_path / source.path
    
    # Détection automatique du type si nécessaire
    src_type = source.type
    if src_type == "auto":
        src_type = detect_source_type(source.path)
    
    print(f"📥 Import: {source.name} ({src_type})")
    
    try:
        if src_type == "tsv":
            questions = import_tsv(src_path, source.name, source.tags)
        elif src_type == "pdf":
            questions = import_pdf(src_path, source.name, source.tags)
        elif src_type == "markdown":
            # Pour les fichiers markdown, on utilise le parser existant
            # (à intégrer depuis build_bank.py)
            print(f"   ℹ️  Markdown non encore supporté, ignoré")
            return []
        else:
            print(f"   ⚠️  Type non supporté: {src_type}")
            return []
        
        print(f"   ✅ {len(questions)} questions importées")
        return questions
        
    except FileNotFoundError as e:
        print(f"   ❌ Fichier non trouvé: {e}")
        return []
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return []


def import_all_sources(config: BankConfig, base_path: Path) -> Dict[str, Any]:
    """
    Importe toutes les sources configurées et génère la banque finale.
    
    Returns:
        Dictionnaire de la banque au format JSON
    """
    all_questions: List[Dict[str, Any]] = []
    stats = {
        "sources_processed": 0,
        "sources_failed": 0,
        "questions_raw": 0,
        "questions_unique": 0,
        "duplicates_removed": 0,
    }
    
    print(f"\n{'='*60}")
    print(f"🏗️  Import multi-sources - {len(config.sources)} sources configurées")
    print(f"{'='*60}\n")
    
    for source in config.sources:
        questions = import_source(source, base_path)
        if questions:
            all_questions.extend(questions)
            stats["sources_processed"] += 1
        else:
            stats["sources_failed"] += 1
    
    stats["questions_raw"] = len(all_questions)
    
    # Déduplication
    print(f"\n{'='*60}")
    print(f"🔍 Déduplication (seuil: {config.similarity_threshold:.0%})")
    print(f"{'='*60}\n")
    
    unique_questions, duplicates = dedupe_questions_advanced(
        all_questions, 
        similarity_threshold=config.similarity_threshold
    )
    
    stats["questions_unique"] = len(unique_questions)
    stats["duplicates_removed"] = len(duplicates)
    
    # Construire la banque finale
    bank = {
        "$schema": "./bank.schema.json",
        "version": "2.0.0",
        "generated": datetime.now().isoformat(),
        "metadata": {
            "sources_count": stats["sources_processed"],
            "questions_count": stats["questions_unique"],
            "duplicates_removed": stats["duplicates_removed"],
        },
        "questions": unique_questions,
    }
    
    # Résumé
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ")
    print(f"{'='*60}")
    print(f"   Sources traitées:    {stats['sources_processed']}")
    print(f"   Sources en échec:    {stats['sources_failed']}")
    print(f"   Questions brutes:    {stats['questions_raw']}")
    print(f"   Doublons éliminés:   {stats['duplicates_removed']}")
    print(f"   Questions finales:   {stats['questions_unique']}")
    print(f"{'='*60}\n")
    
    return bank


def save_bank(bank: Dict[str, Any], output_path: str | Path) -> None:
    """Sauvegarde la banque au format JSON."""
    import json
    
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Banque sauvegardée: {path}")


def main(config_path: str, base_path: Optional[str] = None) -> None:
    """Point d'entrée principal."""
    config = load_config(config_path)
    
    if base_path:
        base = Path(base_path)
    else:
        base = Path(config_path).parent
    
    bank = import_all_sources(config, base)
    save_bank(bank, base / config.output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python source_manager.py <sources.yaml> [base_path]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    base = sys.argv[2] if len(sys.argv) > 2 else None
    main(config_file, base)
