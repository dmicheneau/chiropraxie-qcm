**Signalement de vulnérabilités**

- Mainteneur principal : @dmicheneau
- Si vous découvrez une vulnérabilité, envoyez un email à dmicheneau (ou ouvrez une issue privée si nécessaire).

**Politique de sécurité recommandée**

- Protégez la branche `main` via GitHub > Settings > Branches :
  - Exiger les revues de pull requests (1+ approbation).
  - Exiger que `CODEOWNERS` approuve les PRs (laisser `Require review from Code Owners`).
  - Activer les vérifications CI obligatoires avant merge (GitHub Actions build).
  - Restreindre qui peut pousser sur `main` (restreindre aux mainteneurs si nécessaire).

- Pour restreindre qui peut créer des releases/merges :
  - Dans Settings > Branches > Protect branch `main`, cochez "Restrict who can push to matching branches" et sélectionnez uniquement les comptes ou équipes autorisés (ex : @dmicheneau).
  - Pour les releases, dans Settings > Manage releases, vous pouvez limiter qui peut publier via l'onglet "Collaborators & teams".

**Dependabot**

- Dependabot est activé (.github/dependabot.yml) pour tenir à jour les dépendances Python, npm et les Actions.

**Remarques**

- Ne stockez jamais de secrets (tokens, clés privées, mots de passe) dans le dépôt. Utilisez GitHub Secrets pour Actions.
- Assurez-vous que les fichiers générés et les environnements virtuels ne sont pas poussés (`.gitignore` contient `.venv-build`, `dist/`, `build/`).
