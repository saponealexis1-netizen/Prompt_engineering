# Exemple réel : demande → GO produit par l'agent (test O1)

Session Claude Code non interactive du 13/10/2026, version 2.1.296, modèle claude-opus-5-5, vérificateur sur Haiku. Fichiers recopiés tels quels depuis la copie de test ; rien n'a été retouché.

## 1. Demande (`livrables/DEMANDE.md`)

> J'ai importé les résultats de 20 matchs amicaux fictifs dans donnees/amicaux.csv et les buts dans donnees/buts.csv. Je veux que Claude Code vérifie que les scores collent avec la liste des buts, sans rien modifier. Tu me prépares ce que je lui envoie ?

## 2. GO produit (`livrables/GO.md`)

````markdown
GO — MATCHS AMICAUX FICTIFS / CONTRÔLE SCORES CONTRE LISTE DES BUTS
**NIVEAU:** BORNÉE

## PURPOSE
Vérifier que le score de chacun des 20 matchs amicaux fictifs de `donnees/amicaux.csv` correspond aux buts listés dans `donnees/buts.csv`, sans rien modifier. Ce GO autorise la lecture et le contrôle, rien d'autre.

## ABSOLUTE BOUNDARY
- Lecture seule : aucun fichier de `donnees/` ni du projet n'est modifié, créé ou supprimé.
- Aucune correction de score ou de but : un écart se signale, il ne se répare pas.
- Aucun accès réseau, aucun push ni merge, aucun commit.
- Le résultat est rendu dans la réponse ; si un fichier de rapport semble nécessaire, son emplacement est À CONFIRMER : demander avant d'écrire.

## 1. LECTURE DES FICHIERS
Relever l'empreinte sha256 des deux fichiers, puis lire leurs en-têtes. Les noms de colonnes (identifiant de match, équipes, score, équipe du but, but contre son camp) sont À CONFIRMER : les décrire tels qu'ils sont, sans les deviner.
Require: si la clé reliant un but à son match est absente ou ambiguë, STOP et poser une seule question.

## 2. CONTRÔLES
1. `amicaux.csv` contient bien 20 matchs, sans identifiant en double.
2. Pour chaque match et chaque équipe : nombre de buts dans `buts.csv` égal au score affiché.
3. Aucun but rattaché à un match ou à une équipe absents de `amicaux.csv`.
4. Un match à 0-0 n'a aucun but listé.
Require: séparer « écart certain » et « information insuffisante » (but contre son camp mal attribuable, ligne illisible) ; ne rien corriger.
Require: chaque contrôle a un témoin négatif fabriqué en mémoire, jamais écrit dans `donnees/`, qui doit échouer, et il échoue bien.

## 3. PREUVE DE NON-MODIFICATION
Relever à nouveau les empreintes sha256 en fin de travail.
Require: empreintes avant et après identiques ; sinon STOP immédiat et signalement.

## FINAL RETURN
En français :
1. Résultats bruts par contrôle (matchs testés, conformes, écarts) avant tout résumé.
2. Tableau des écarts : match, équipe, score affiché, buts comptés, statut.
3. Informations insuffisantes, séparées des écarts certains.
4. Résultat des témoins négatifs et empreintes avant et après.
5. Ce qui reste à décider par un humain.

**STOP après le rapport. Aucune modification des données, aucun commit, aucun push.**
````

## 3. Contrôle de forme (sortie du script)

```json
{
  "status": "CONFORME_STRUCTURE",
  "niveau": "BORNEE",
  "mots": 375,
  "budget": 600,
  "sections_numerotees": 3,
  "require": 4,
  "commandes_dangereuses": [],
  "identifiants_inconnus": [],
  "erreurs": []
}
```

## 4. Verdict du sous-agent vérificateur

```
VERDICT: CONFORME
NIVEAU_ATTENDU: BORNÉE | NIVEAU_DU_GO: BORNÉE
ECARTS: Mineur. Le GO n'autorise pas la lecture de secrets (pas d'autorisation, donc conforme), mais il ne l'interdit pas explicitement comme le demande la grille. Le format du skill `foot-go` n'a pas été vérifié, faute d'avoir lu ses `references/`. Le GO respecte le reste : les 20 matchs, `amicaux.csv` et `buts.csv`, la lecture seule, les empreintes sha256 avant et après, les noms de colonnes marqués « À CONFIRMER », et une dernière ligne STOP.
CORRECTION_MINIMALE: Ajouter dans ABSOLUTE BOUNDARY une ligne « Aucune lecture de secret (`.env`, identifiants, clés) et aucun accès réseau. »
```
