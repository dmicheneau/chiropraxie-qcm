**Lancer l'interface QCM (version web, hors‑ligne)**

- Le contenu web est maintenant dans le dossier `web/`.
- Pour utiliser l'application (aucune installation nécessaire) :

- Double‑cliquez sur : `web/web_qcm/offline_qcm.html` — cela ouvrira l'interface dans votre navigateur par défaut.

- Alternative (via le terminal) :

```bash
# Ouvrir dans le navigateur par défaut
open web/web_qcm/offline_qcm.html

# Ou lancer un petit serveur local (si votre navigateur bloque certains appels file://)
cd web
python3 -m http.server 8000
# puis ouvrez http://localhost:8000/web_qcm/offline_qcm.html
```

Notes
- J'ai supprimé la partie Go et les binaires non fonctionnels. Le dépôt contient désormais uniquement la partie web et les sources QCM.
- Si vous souhaitez que j'ajoute un bref `README` dans `web/` ou que je réorganise davantage (par ex. `web/decks`, `web/docs`), dites‑le et je l'applique.

---

## Banque JSON (multi‑réponses / Vrai‑Faux / images)

Le lecteur actuel supporte un mode **"Quiz (généré)"** qui charge `web/bank/quiz.json` via `fetch()`.
Cela nécessite généralement un **serveur local** (les navigateurs bloquent souvent `file://`).

### 1) Construire la banque canonique

```bash
python3 bank/build_bank.py --include-generated --include-existing-decks
```

Génère : `web/bank/bank.json` (non versionné par défaut via `.gitignore`).

### 2) Générer un quiz aléatoire par thème (tag)

```bash
# Exemple : 20 questions d'Angiologie
python3 bank/generate_quiz.py --tag Angiologie --count 20 --seed 42
```

Génère : `web/bank/quiz.json`

### 3) Lancer le lecteur (mode serveur)

```bash
cd web
python3 -m http.server 8000
# puis ouvrez http://localhost:8000/web_qcm/index.html
```

### Extraire du texte depuis un PDF (optionnel)

Ce dépôt inclut un extracteur PDF simple (optionnel) : `bank/extract_pdf_text.py`.

```bash
pip install pymupdf
python3 bank/extract_pdf_text.py "/chemin/vers/cours.pdf" --out sources/cours.txt
```
