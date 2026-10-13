GO — LIGUE DÉMO / RECALCUL DES MINUTES JOUÉES — PRÉPARATION ET VALIDATION PILOTE
**NIVEAU:** CRITIQUE

## PURPOSE
Réécrire le calcul des minutes jouées et le valider sur les 12 matchs pilotes avant toute utilisation sur la saison. Les minutes alimentent les indicateurs de forme des joueurs : une erreur ici fausserait tout ce qui est calculé ensuite. Ce GO autorise la préparation et le pilote, rien de plus.

## ABSOLUTE BOUNDARY
- Aucun recalcul sur la saison complète : il exigera un GO séparé.
- Les données sources de `donnees/` restent inchangées ; leurs empreintes sha256 sont relevées avant et après.
- Aucune correction implicite d'une minute, d'un rôle ou d'un événement : un écart se signale, il ne se répare pas.
- Aucun accès réseau, aucun push ni merge ; commit local seulement après validation.

## 1. RÉFÉRENCE GELÉE
Relever les minutes actuelles des 12 matchs pilotes dans `sorties/minutes/reference.csv`.
Require: empreintes des fichiers sources notées avant toute exécution.

## 2. NOUVEAU CALCUL
Écrire le calcul dans `outils/minutes.py` : titulaire non remplacé = 90 ; titulaire remplacé = minute de sortie ; entrant = 90 moins la minute d'entrée ; temps additionnel ignoré.
Require: une règle écrite par cas ; un cas non couvert renvoie « INCONNU », jamais une valeur devinée.

## 3. CONTRÔLES
1. Régression : sur les 12 matchs, nouveau calcul égal à la référence, ou chaque écart expliqué ligne par ligne.
2. Vérificateur indépendant : un second script, écrit sans importer `outils/minutes.py`, recalcule et compare.
3. Contrôles négatifs : trois erreurs volontaires (sortie avant l'entrée, minute illisible, joueur en double) doivent être détectées.
4. Déterminisme : deux exécutions donnent des sorties identiques à l'octet.
Require: chaque contrôle qui passe doit passer pour la bonne raison ; montrer qu'il échoue sur une donnée fausse.

## 4. CONDITIONS D'ARRÊT
- Écart inexpliqué, contrôle négatif non détecté ou empreinte source modifiée : STOP immédiat, rapport, aucune correction.
- Information manquante pour une règle : poser une seule question, ne rien supposer.

## FINAL RETURN
En français :
1. Statut : VALIDÉ_PILOTE, PARTIEL ou ÉCHEC.
2. Preuve brute avant le résumé : écarts, résultats des contrôles, empreintes avant et après.
3. Risques restants et ce qui n'a pas été testé.
4. Décisions humaines restantes et GO suivant proposé.

**STOP après le pilote : validation humaine requise avant tout recalcul de la saison. Aucun push.**
