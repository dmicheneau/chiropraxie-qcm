#!/usr/bin/env python3
import sys
import random
import json
import re
import unicodedata
from pathlib import Path

def normalize_for_match(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def load_existing_prompts(bank_path: Path) -> set:
    if not bank_path.exists():
        return set()
    try:
        with open(bank_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {normalize_for_match(q["prompt"]) for q in data.get("questions", [])}
    except Exception as e:
        print(f"Erreur lors du chargement de la banque: {e}")
        return set()

def convert_tsv_to_deck(tsv_path: Path, deck_name: str, tag: str, bank_path: Path):
    if not tsv_path.exists():
        print(f"Erreur: {tsv_path} n'existe pas.")
        return

    existing_prompts = load_existing_prompts(bank_path)
    
    lines = tsv_path.read_text(encoding="utf-8").splitlines()
    pairs = []
    for line in lines:
        if "\t" in line:
            term, definition = line.split("\t", 1)
            pairs.append((term.strip(), definition.strip().replace("\\n", "\n")))

    if not pairs:
        print("Aucune donnée trouvée dans le TSV.")
        return

    # Filtrer les doublons
    new_pairs = []
    duplicates_count = 0
    for term, definition in pairs:
        if normalize_for_match(term) in existing_prompts:
            duplicates_count += 1
            continue
        new_pairs.append((term, definition))
    
    print(f"Doublons ignorés: {duplicates_count}")
    if not new_pairs:
        print("Toutes les questions sont déjà présentes dans la banque.")
        return

    # Générer le Markdown
    md_output = f"# Deck: {deck_name} — {len(new_pairs)} questions\n\n"
    md_output += "**Consigne** : 1 seule bonne réponse (A–D).\n\n"
    
    tsv_answers = ""
    
    all_definitions = [p[1] for p in pairs] # Utiliser toutes les définitions pour les distracteurs

    for i, (term, definition) in enumerate(new_pairs, 1):
        # Choisir 3 distracteurs
        distractors = random.sample([d for d in all_definitions if d != definition], min(3, len(all_definitions)-1))
        while len(distractors) < 3:
            distractors.append("Réponse D (par défaut)")
            
        choices = [definition] + distractors
        random.shuffle(choices)
        
        correct_letter = chr(65 + choices.index(definition))
        
        md_output += f"{i}) {term} [Tags: {tag}]\n"
        for j, choice in enumerate(choices):
            letter = chr(65 + j)
            # Nettoyer le choix pour qu'il tienne sur une ligne si possible
            choice_clean = choice.replace("\n", " / ")
            md_output += f"- {letter}. {choice_clean}\n"
        md_output += "\n"
        
        tsv_answers += f"{term}\t{correct_letter}\n"

    # Sauvegarder les fichiers
    repo_root = Path(__file__).parent.parent
    deck_file = repo_root / "web" / "decks" / f"Deck_{tag}.md"
    ans_file = repo_root / "web" / "decks" / f"Quizlet_{tag}.tsv"
    
    deck_file.write_text(md_output, encoding="utf-8")
    ans_file.write_text(tsv_answers, encoding="utf-8")
    
    print(f"Fichiers générés:\n- {deck_file}\n- {ans_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 convert_tsv_to_deck.py <tsv_file> <deck_title> <tag>")
        sys.exit(1)
    
    tsv_file = Path(sys.argv[1])
    title = sys.argv[2]
    tag = sys.argv[3]
    bank = Path(__file__).parent.parent / "web" / "bank" / "bank.json"
    
    convert_tsv_to_deck(tsv_file, title, tag, bank)
