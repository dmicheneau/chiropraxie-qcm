**QCM Chiropraxie**

Ce dépôt contient une banque de QCM pour révision par thèmes et une petite application web locale pour lancer des quiz.

**Pré-requis**:
- Python 3.9+ (interpréteur système)

**Fichiers importants**:
- **Usage**: [start_qcm.py](start_qcm.py) — lance un serveur HTTP local et ouvre l'interface web.
- Interface: [app.html](app.html) — application web cliente (ouvre via le serveur).
- Banque: [web/bank/bank.json](web/bank/bank.json) — fichier JSON généré contenant les questions.
- Génération de banque: [bank/build_bank.py](bank/build_bank.py) — script pour construire la banque depuis les decks et générateurs.

**Lancer l'application (local)**
1. Depuis la racine du dépôt, lancez :

```bash
python3 start_qcm.py
```

2. Le script démarre un serveur (par défaut port libre, affiche l'URL) et ouvre `app.html` dans le navigateur.

Sur macOS, il existe un lanceur double‑clic :

```bash
./start_qcm.command
```

**Recréer / Mettre à jour la banque de questions**

Le script `bank/build_bank.py` peut regrouper les questions depuis :
- les fichiers Markdown dans `web/decks/Deck_*.md` (décks existants),
- le générateur `generate_qcm_400.py` (questions générées),
- d'autres importeurs présents dans `bank/importers/`.

Exemple rapide pour reconstruire `web/bank/bank.json` depuis la racine du dépôt :

```bash
python3 - <<'PY'
from pathlib import Path
from bank.build_bank import build_from_existing_decks, build_from_generate_qcm_400
import json
from datetime import datetime, timezone

repo_root = Path('.')
deck_questions = build_from_existing_decks(repo_root)
gen_questions = build_from_generate_qcm_400(repo_root)
all_questions = deck_questions + gen_questions
bank = {
  'version': '2.1.0',
  'generated': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
  'metadata': {'questions_count': len(all_questions)},
  'questions': all_questions
}
Path('web/bank/bank.json').write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding='utf-8')
print('web/bank/bank.json mis à jour')
PY
```

Remarque: `build_from_existing_decks()` lit les `Deck_*.md` (format attendu: num) et tente d'inférer la clé réponse via fichiers TSV associés si présents.

**Débogage courant**
- Si l'interface n'affiche pas de choix : vérifier que `web/bank/bank.json` contient des questions `single_choice`/`multiple_choice` avec un tableau `choices` (A–D).
- Regarder la console du navigateur (DevTools) pour les erreurs JS. Messages fréquents : éléments manquants référencés par l'UI (corriger `app.html`).
- Pour reconstruire la banque, supprimez l'ancien `web/bank/bank.json` puis relancez la commande ci‑dessus.

**Tests manuels rapides**
1. Reconstruire la banque (voir commande ci‑dessus).
2. Lancer `python3 start_qcm.py` et ouvrir l'URL affichée.
3. Sélectionner un thème, vérifier que les questions affichent 4 choix (A–D).

**Contribuer / Ajouter des decks**
- Ajouter un fichier `web/decks/Deck_Nom.md` au format existant (liste numérotée avec `- A.` / `- B.` / ...)
- Optionnel : fournir `web/decks/Quizlet_Nom.tsv` pour fournir la clé des réponses si elle manque dans le markdown.

Si vous voulez, je peux :
- ajouter un script `bin/rebuild_bank.sh` pour automatiser la reconstruction, ou
- committer et pousser ces changements directement.

---
Merci — dites-moi si vous souhaitez que j'ajoute des badges, des exemples supplémentaires, ou que je crée un script de build automatisé.
