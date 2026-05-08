# Suivi GitHub Push / Merge

Ce fichier sert a noter les changements faits en local avant de tout envoyer sur GitHub.

## Objectif

- Travailler et tester les modifications en local.
- Noter les fichiers modifies et la raison des changements.
- Preparer un commit propre.
- Garder les commandes utiles pour push ou merge plus tard.

## Changements a suivre

| Date | Fichier / dossier | Changement | Statut |
| --- | --- | --- | --- |
| 2026-05-04 | fichiers utiles/github_push.md | Creation du fichier de suivi GitHub push/merge | Fait |
| 2026-05-04 | app/pages/login.py | Refonte visuelle de la page de connexion : logo AGIL centre, fond jaune avec texte gris fonce, polices agrandies, formulaire et bouton ameliores | Fait |
| 2026-05-04 | app/pages/login.py | Amelioration de la visibilite du bouton afficher/masquer le mot de passe | Fait |
| 2026-05-04 | app/components/ui.py | Refonte du socle visuel global : police Manrope, palette AGIL harmonisee, cartes, boutons, inputs, filtres, tableaux et graphiques | Fait |
| 2026-05-04 | app/components/ui.py | Correction de la navbar : bouton Deconnexion aligne avec la navigation, hauteur et etats actifs harmonises | Fait |
| 2026-05-04 | .streamlit/config.toml | Ajout d'un theme Streamlit clair pour eviter les tableaux noirs et uniformiser les couleurs natives | Fait |
| 2026-05-04 | app/pages/accueil.py | Refonte de la page accueil avec header AGIL, cartes modules et blocs architecture bases sur les composants communs | Fait |
| 2026-05-04 | app/pages/tableau_de_bord.py | Harmonisation des titres et correction visuelle des filtres via le CSS global | Fait |
| 2026-05-04 | app/pages/previsions.py | Harmonisation des libelles et correction du tableau detail mensuel via theme clair et CSS global | Fait |
| 2026-05-04 | app/pages/exploration.py | Harmonisation de la page exploration et correction des tableaux via theme clair et CSS global | Fait |
| 2026-05-04 | app/pages/analyse_historique.py | Harmonisation des titres visibles avec le nouveau socle visuel | Fait |
| 2026-05-04 | app/pages/agent_ia.py | Refonte des cartes de recommandations et harmonisation des boutons/actions | Fait |
| 2026-05-04 | app/pages/chatbot.py | Harmonisation des libelles de la page chatbot et conservation du style global commun | Fait |
| 2026-05-04 | app/components/ui.py | Correction des tableaux blanc sur blanc, des tags multiselect avec rectangle blanc et du contraste des icones actives dans la navbar | Fait |
| 2026-05-04 | app/components/ui.py, app/pages/previsions.py, app/pages/exploration.py, app/pages/agent_ia.py | Remplacement des st.dataframe par un tableau HTML AGIL pour garantir un rendu lisible et clair | Fait |
| 2026-05-04 | app/components/ui.py | Suppression du vide au-dessus de la navbar et harmonisation des couleurs : icones/textes jaunes hors selection, gris fonce quand selectionnes | Fait |
| 2026-05-04 | config.py | Nettoyage de la configuration et passage du split ML a train 2015-2016, test 2017, 2018 exclue de l'evaluation principale | Fait |
| 2026-05-04 | ml/arima_forecast.py | Ajout du modele SARIMAX avec cours Brent exogene, evaluation 2017, entrainement final 2015-2017 et prevision future | Fait |
| 2026-05-04 | run_ml.py | Refonte du pipeline ML pour comparer Prophet vs SARIMAX, generer model_comparison.csv, best_model.json et predictions_test.csv | Fait |
| 2026-05-04 | ml/forecast.py | Adaptation de Prophet au split 2015-2016 / 2017 et entrainement final sans 2018 | Fait |
| 2026-05-04 | app/pages/previsions.py | Page Previsions branchee sur le modele retenu automatiquement et affichage du tableau comparatif Prophet vs SARIMAX | Fait |
| 2026-05-04 | app/pages/agent_ia.py, app/agent/context.py | Compatibilite Agent IA avec les nouvelles metriques multi-modeles et les predictions du modele retenu | Fait |
| 2026-05-04 | requirements.txt | Ajout de statsmodels pour SARIMAX | Fait |
| 2026-05-04 | ml/model_comparison.csv, ml/best_model.json, ml/predictions_test.csv, ml/sarima_model.pkl, ml/prophet_model.pkl, ml/metriques.pkl | Artefacts ML regeneres : SARIMAX retenu avec MAPE 6.83 contre 12.29 pour Prophet sur 2017 | Fait |

## Checklist avant push

- [ ] Verifier les fichiers modifies avec `git status`
- [ ] Relire les changements importants avec `git diff`
- [ ] Tester l'application localement
- [ ] Ajouter les fichiers avec `git add .`
- [ ] Creer un commit avec un message clair
- [ ] Push sur GitHub

## Commandes utiles

Voir les fichiers modifies :

```powershell
git status
```

Voir le detail des changements :

```powershell
git diff
```

Ajouter tous les changements :

```powershell
git add .
```

Creer un commit :

```powershell
git commit -m "Description courte des modifications"
```

Envoyer sur GitHub :

```powershell
git push
```

Si la branche n'est pas encore liee a GitHub :

```powershell
git push -u origin main
```

## Notes pour merge

Avant de merge une branche :

```powershell
git status
git pull
```

Puis merge la branche voulue :

```powershell
git merge nom-de-la-branche
```

En cas de conflit :

- Ouvrir les fichiers indiques par Git.
- Corriger les zones de conflit.
- Relancer les tests.
- Finaliser avec :

```powershell
git add .
git commit
```
