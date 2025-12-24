#!/usr/bin/env python3
"""
Script pour reconstruire les QCM d'embryologie à partir des flashcards Quizlet.

Les flashcards originales sont converties en QCM avec 4 réponses :
- 1 bonne réponse (la réponse originale de la flashcard)
- 3 distracteurs générés intelligemment à partir d'autres réponses du même deck
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any

def load_tsv_flashcards(tsv_path: Path) -> List[tuple]:
    """Charge les flashcards depuis un fichier TSV."""
    flashcards = []
    with open(tsv_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                question = parts[0].strip()
                answer = parts[1].strip()
                if question and answer:
                    flashcards.append((question, answer))
    return flashcards

def generate_distractors(correct_answer: str, all_answers: List[str], count: int = 3) -> List[str]:
    """Génère des distracteurs pertinents pour une question."""
    # Filtrer les réponses trop similaires ou trop longues
    candidates = [ans for ans in all_answers if ans != correct_answer and len(ans) < 200]
    
    # Si pas assez de candidats, on prend ce qu'on a
    if len(candidates) < count:
        return candidates
    
    # Sélectionner des distracteurs de longueur similaire à la bonne réponse
    correct_len = len(correct_answer)
    scored = []
    for ans in candidates:
        # Score basé sur la différence de longueur (plus proche = mieux)
        length_diff = abs(len(ans) - correct_len)
        # Éviter les réponses qui sont des questions
        is_question = '?' in ans
        score = length_diff + (1000 if is_question else 0)
        scored.append((score, ans))
    
    # Trier par score et prendre les meilleurs
    scored.sort()
    return [ans for _, ans in scored[:count]]

def create_qcm_from_flashcard(question: str, answer: str, all_answers: List[str], qcm_id: str) -> Dict[str, Any]:
    """Crée une question QCM à partir d'une flashcard."""
    # Générer 3 distracteurs
    distractors = generate_distractors(answer, all_answers, 3)
    
    # Créer la liste des choix avec la bonne réponse
    all_choices = [answer] + distractors
    
    # Compléter avec des réponses génériques si pas assez de distracteurs
    generic_answers = [
        "Cette information n'est pas correcte",
        "Aucune de ces réponses",
        "Information non pertinente",
        "Réponse incorrecte"
    ]
    
    while len(all_choices) < 4:
        all_choices.append(generic_answers[len(all_choices) - 1])
    
    # Limiter à 4 choix
    all_choices = all_choices[:4]
    
    # Mélanger les choix
    random.shuffle(all_choices)
    
    # Trouver la position de la bonne réponse
    correct_key = ['A', 'B', 'C', 'D'][all_choices.index(answer)]
    
    # Créer les choix au format JSON
    choices = []
    for i, choice_text in enumerate(all_choices):
        choices.append({
            "key": ['A', 'B', 'C', 'D'][i],
            "text": choice_text
        })
    
    return {
        "id": qcm_id,
        "type": "single_choice",
        "prompt": question,
        "choices": choices,
        "tags": ["Embryologie"],
        "source": {
            "kind": "quizlet_rebuilt",
            "ref": "sources/quizlet_embryo_semestriel.tsv"
        },
        "answer": {
            "answers": [correct_key]
        },
        "explanation": "Question reconstruite à partir de Quizlet"
    }

def main():
    # Chemins
    base_path = Path(__file__).parent.parent
    tsv_embryo = base_path / "sources" / "quizlet_embryo_semestriel.tsv"
    tsv_embryologie = base_path / "sources" / "quizlet_embryologie.tsv"
    bank_path = base_path / "web" / "bank" / "bank.json"
    
    print("🔄 Reconstruction des QCM d'embryologie...")
    
    # Charger les flashcards des deux sources
    flashcards = []
    if tsv_embryo.exists():
        print(f"📖 Lecture de {tsv_embryo.name}...")
        flashcards.extend(load_tsv_flashcards(tsv_embryo))
    
    if tsv_embryologie.exists():
        print(f"📖 Lecture de {tsv_embryologie.name}...")
        flashcards.extend(load_tsv_flashcards(tsv_embryologie))
    
    print(f"✅ {len(flashcards)} flashcards chargées")
    
    # Extraire toutes les réponses pour générer des distracteurs
    all_answers = [ans for _, ans in flashcards]
    
    # Générer les QCM
    print("🎯 Génération des QCM...")
    new_questions = []
    for idx, (question, answer) in enumerate(flashcards, 1):
        qcm_id = f"embryologie_rebuilt_{idx:04d}"
        qcm = create_qcm_from_flashcard(question, answer, all_answers, qcm_id)
        new_questions.append(qcm)
    
    print(f"✅ {len(new_questions)} QCM générés")
    
    # Charger la banque actuelle
    print("📂 Chargement de la banque actuelle...")
    with open(bank_path, 'r', encoding='utf-8') as f:
        bank_data = json.load(f)
    
    # Supprimer les anciennes questions d'embryologie
    original_count = len(bank_data['questions'])
    bank_data['questions'] = [
        q for q in bank_data['questions']
        if 'Embryo_Semestriel' not in q.get('tags', []) and 'Embryologie' not in q.get('tags', [])
    ]
    removed = original_count - len(bank_data['questions'])
    print(f"🗑️  {removed} anciennes questions d'embryologie supprimées")
    
    # Ajouter les nouvelles questions
    bank_data['questions'].extend(new_questions)
    bank_data['metadata']['questions_count'] = len(bank_data['questions'])
    
    # Sauvegarder
    print("💾 Sauvegarde de la banque...")
    with open(bank_path, 'w', encoding='utf-8') as f:
        json.dump(bank_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✨ Terminé !")
    print(f"📊 Nouvelle banque : {len(bank_data['questions'])} questions")
    print(f"🎓 Embryologie : {len(new_questions)} QCM")

if __name__ == "__main__":
    main()
