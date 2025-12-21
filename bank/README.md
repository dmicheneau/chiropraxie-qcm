# Banque QCM (format canonique)

Ce dossier définit le **format canonique** des questions.

- Schéma JSON : `bank.schema.json`
- Export attendu (par défaut) : `web/bank/bank.json`

## Types de questions

- `single_choice` : 1 seule bonne réponse
- `multiple_choice` : plusieurs bonnes réponses (ordre indifférent)
- `true_false` : Vrai/Faux (2 choix)

## Images

Les images sont référencées via `media[]` (niveau question) et/ou `choices[].media[]` (niveau choix), avec un `src` pointant vers un fichier local (ex: `assets/plexus.png`).

## Note importante (sources)

Ce format inclut `source` et `tags` pour tracer l’origine et classer les questions.
