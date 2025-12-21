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
