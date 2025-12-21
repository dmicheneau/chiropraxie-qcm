# QCM Web Player

Fichiers créés:
- `index.html` — interface web (intègre les decks Markdown)
- `qcm.js` — logique de parsing, navigation, scoring
- `style.css` — styles simples

Pré-requis:
Ouvrir la version hors-ligne (sans serveur)

1) Ouvrir directement le fichier `web_qcm/offline_qcm.html` dans un navigateur web (double-cliquer ou glisser-déposer) — aucune commande serveur nécessaire.

2) Choisir un deck dans la liste, cliquer sur « Charger le deck », répondre aux questions, puis cliquer sur « Soumettre » pour voir le score et le corrigé.

Remarque: la page embarque les decks et les clés de correction; si vous souhaitez une exportation différente (Anki, PDF), dites-moi quel format vous voulez.

Utilisation:
- Choisir un deck et cliquer sur « Démarrer »
- Répondre aux questions, naviguer avec « Suivant » / « Précédent »
- Cliquer sur « Terminer » pour obtenir le taux (s’applique aux questions dont la clé est présente dans le TSV)
- Cliquer sur « Vérifier les réponses » pour afficher la correction par item
