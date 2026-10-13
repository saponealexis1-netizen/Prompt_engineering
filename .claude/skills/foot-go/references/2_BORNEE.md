GO — LIGUE DÉMO / CONTRÔLE DES COMPOSITIONS SUR 12 MATCHS PILOTES
**NIVEAU:** BORNÉE

## PURPOSE
Vérifier la cohérence des compositions (titulaires, remplaçants, remplacements) sur les 12 matchs pilotes de `donnees/pilote/`, sans rien corriger. Le résultat servira à décider si le contrôle peut être étendu à la saison.

## ABSOLUTE BOUNDARY
- Lecture seule sur `donnees/` : aucune correction de minute, de rôle ou d'événement.
- Uniquement les 12 matchs pilotes ; aucun traitement de la saison complète.
- Aucun accès réseau, aucun push ni merge.
- Écriture autorisée seulement dans `sorties/controle_compos/`.

## 1. CONTRÔLES À CODER
1. Exactement 11 titulaires par équipe et par match.
2. Aucun joueur listé deux fois sur la même feuille de match.
3. Chaque remplaçant entré a un remplacement associé, et inversement.
Require: chaque contrôle a un témoin négatif, un cas fabriqué qui doit échouer, et le témoin échoue bien.

## 2. EXÉCUTION SUR LE PILOTE
Lancer les trois contrôles sur les 12 matchs.
Require: séparer « anomalie certaine » et « information insuffisante » ; ne rien corriger.

## 3. RAPPORT
Écrire `sorties/controle_compos/rapport.csv` : match, équipe, contrôle, statut, détail.

## FINAL RETURN
En français :
1. Résultats bruts par contrôle (cas testés, conformes, anomalies) avant tout résumé.
2. Anomalies certaines et informations insuffisantes, séparées.
3. Résultat des témoins négatifs.
4. Recommandation : étendre ou non à la saison, et ce qui reste à décider.

**STOP après le rapport. Aucune correction des données, aucun push.**
