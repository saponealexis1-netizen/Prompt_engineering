---
name: foot-go
description: Rédige un prompt GO pour Claude Code (le texte d'instructions que l'utilisateur va lui transmettre) sur une tâche de données football, en s'inspirant des prompts de référence de l'équipe. À utiliser quand l'utilisateur veut préparer, écrire ou remettre au propre ce qu'il va demander à Claude Code : contrôle, correction, phase technique. Ne pas utiliser pour exécuter la tâche, écrire du code, analyser des cotes, prédire un match ou répondre à une question sur le football.
---

# Skill — Foot GO

## Objectif
Produire `livrables/GO.md` : un prompt adapté à la demande, avec la structure, la méthode et le niveau de détail des prompts de référence, que l'utilisateur pourra transmettre tel quel à Claude Code.
Un bon GO couvre chaque élément de la demande, n'invente rien, fixe des limites claires et dit quand s'arrêter.

## Étapes
1. Enregistrer la demande mot pour mot dans `livrables/DEMANDE.md`.
2. Choisir le niveau selon l'impact réel, pas selon la longueur de la demande :
   - CIBLÉE : petite modification sans risque ;
   - BORNÉE : phase technique limitée et réversible ;
   - CRITIQUE : touche des données ou des calculs dont dépend la suite, ou une action difficile à annuler.
3. Lire les trois références de `references/` (1_CIBLEE, 2_BORNEE, 3_CRITIQUE) : reprendre ce qui est constant (structure, méthode, garde-fous), adapter ce qui varie (longueur, nombre de sections). Ne reprendre ni leur sujet, ni leurs fichiers, ni leurs chiffres.
4. Rédiger `livrables/GO.md` au format ci-dessous.
5. Lancer `python .claude/skills/foot-go/scripts/check_prompt.py livrables/GO.md livrables/DEMANDE.md`. La forme est jugée par ce script, pas par une estimation.
6. Demander au sous-agent `verificateur` de comparer `livrables/GO.md` à `livrables/DEMANDE.md`, en ne lui donnant que ces deux chemins : ni ton niveau, ni ton avis, pour ne pas l'orienter.
7. Si le script ou le vérificateur échoue : une seule correction ciblée, puis relancer les deux.

## Règles
- Un fait absent de la demande (commit, fichier, chiffre, résultat) est écrit « À CONFIRMER », jamais inventé.
- Information manquante qui change le niveau ou le périmètre : poser une seule question avant d'écrire. Sinon, la noter « À CONFIRMER ».
- Le GO n'autorise jamais push, merge, suppression de données, lecture de secrets ni appel réseau. Une action irréversible ou un traitement complet se prépare puis s'arrête avant : STOP et validation humaine.
- Demande d'exécution, d'action dangereuse ou de secret : ne pas écrire de GO, refuser en une phrase et proposer au besoin un GO de préparation (voir `references/CAS_REFUSE.md`).
- Longueur proportionnée : CIBLÉE ≤ 250 mots, BORNÉE ≤ 600, CRITIQUE ≤ 1 000.

## Format
- Ligne 1 : `GO — <PROJET> / <ACTION>`. Ligne 2 : `**NIVEAU:** CIBLÉE`, `BORNÉE` ou `CRITIQUE`.
- `## PURPOSE`, puis des sections numérotées `## 1. ...`, puis `## FINAL RETURN`.
- BORNÉE et CRITIQUE ajoutent `## ABSOLUTE BOUNDARY` et des lignes `Require:` (au moins une ; deux en CRITIQUE, avec une section de contrôles).
- Dernière ligne : `**STOP ...**`, avec ce qui reste interdit.
