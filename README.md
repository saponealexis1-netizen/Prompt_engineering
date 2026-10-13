# Foot GO Agent — prototype pédagogique (Prompt Engineering, module 4)

À partir d'une demande en langage naturel, cet agent Claude Code rédige un nouveau prompt « GO » pour Claude Code, en s'inspirant de trois prompts de référence (few-shot, module 3) : même structure, même méthode, niveau de détail proportionné à l'impact (CIBLÉE, BORNÉE ou CRITIQUE). Il n'exécute jamais le prompt qu'il écrit. Un script vérifie la forme, un sous-agent vérifie le fond.

**Statut :** prototype réalisé pour un cours de Prompt Engineering, testé le 13/10/2026 avec Claude Code 2.1.296. Ce n'est pas un outil de production. Les prompts de référence, les données et les exemples sont fictifs : ce dépôt ne contient aucun fichier ni aucune donnée d'un vrai projet.

## Contenu

```
Prompt_engineering/
├── README.md                          présentation, installation, tests, limites
├── CLAUDE.md                          fiche de poste : mission, droits, interdits, méthode, arrêt
├── .gitignore                         exclut secrets, réglages locaux, caches et sorties de l'agent
├── .claude/
│   ├── settings.json                  permissions : allow / deny, en Bash et en PowerShell
│   ├── agents/verificateur.md         sous-agent Haiku, lecture seule
│   └── skills/foot-go/
│       ├── SKILL.md                   la méthode de rédaction (déclenchée par sa description)
│       ├── references/                3 prompts de référence fictifs + 1 cas refusé
│       └── scripts/check_prompt.py    contrôle déterministe de la forme
├── livrables/                         DEMANDE.md et GO.md produits par l'agent (non versionnés)
├── data/EXEMPLE_FICTIF.txt            donnée factice, cible des tests rouges
└── tests/                             tests unitaires, GO piégé, fiche de tests, exemple réel
```

## Fonctionnement

1. L'agent enregistre la demande mot pour mot dans `livrables/DEMANDE.md`.
2. Il choisit le niveau selon l'impact réel de la tâche.
3. Il lit les trois références et en reprend la structure et la méthode, pas le contenu.
4. Il écrit `livrables/GO.md`.
5. Le script contrôle la forme : titre, niveau, sections, lignes `Require:`, ligne STOP, longueur, commandes dangereuses, identifiants absents de la demande.
6. Le sous-agent `verificateur` compare le GO à la demande : éléments couverts, niveau, rien d'inventé, limites.
7. Script et vérificateur conformes : le GO final est affiché, puis STOP. Sinon, une seule correction, puis STOP avec l'explication.

## Installation

Prérequis : Claude Code (terminal ou extension VS Code) connecté à un compte, Git, et Python 3 (testé avec 3.14 ; bibliothèque standard seulement, rien à installer).

1. Cloner le dépôt et entrer dans le dossier :
   ```
   git clone https://github.com/saponealexis1-netizen/Prompt_engineering.git
   cd Prompt_engineering
   ```
2. Facultatif, conseillé avant les tests de déclenchement : créer `.claude/settings.local.json` pour désactiver les plugins de la machine dans ce dossier (voir « Isolation des tests »).
3. Ouvrir ce dossier seul (VS Code ou terminal) ; `pwd` doit se terminer par `Prompt_engineering`.
4. Lancer `claude` en mode standard (jamais `bypassPermissions`) et accepter de faire confiance au dossier.
5. Vérifier avec `/skills` que `foot-go` apparaît, et avec `/agents` que `verificateur` apparaît.

## Utilisation

Formuler la demande naturellement, par exemple : « J'ai importé les résultats de 20 matchs amicaux fictifs dans donnees/amicaux.csv et les buts dans donnees/buts.csv. Je veux que Claude Code vérifie que les scores collent avec la liste des buts, sans rien modifier. Tu me prépares ce que je lui envoie ? »

L'agent écrit `livrables/DEMANDE.md` et `livrables/GO.md`, lance le script, consulte le vérificateur, puis affiche le GO final ou explique pourquoi il ne peut pas le valider. Claude Code peut demander l'autorisation d'écrire un fichier ou de lancer le script : lire la demande avant d'accepter. Exemple complet, de la demande au verdict du vérificateur : `tests/exemple_reel_O1.md`.

## Isolation des tests

Les plugins installés pour tout l'ordinateur se chargeraient aussi dans ce dossier et fausseraient les tests de déclenchement. On les désactive pour ce dossier seulement, dans `.claude/settings.local.json` (non versionné ; la configuration globale n'est pas modifiée) :

```json
{ "enabledPlugins": { "superpowers@claude-plugins-official": false, "pdf-viewer@synced": false } }
```

Chaque machine adapte la liste à ses propres plugins (commande `/plugin`). Les skills personnels de `~/.claude/skills` et les skills intégrés de Claude Code restent visibles : les tests mesurent donc `foot-go` en concurrence avec eux.

## Tests

Depuis la racine du dépôt :

- `python -m unittest discover -s tests -v` : tests du validateur et de la configuration (sans réseau, sans Claude Code).
- `python .claude/skills/foot-go/scripts/check_prompt.py .claude/skills/foot-go/references/2_BORNEE.md` : contrôle de forme d'un GO (code de sortie 0 = conforme, 1 = non conforme, 2 = mauvais usage).
- `python .claude/skills/foot-go/scripts/check_prompt.py tests/piege/GO.md tests/piege/DEMANDE.md` : le GO piégé passe le contrôle de forme ; seul le vérificateur voit qu'il trahit la demande.
- `tests/FICHE_TESTS.md` : déclenchement 5/3/2, six tests rouges, comparaison avec et sans skill, conditions d'arrêt, vérificateur ; résultats observés et tests restant à faire.

## Limites

- Prototype pédagogique, pas un outil de production : aucune garantie, à n'utiliser que sur des données fictives ou de test.
- Le script juge la forme, le vérificateur juge le fond. Aucun des deux ne garantit la vérité.
- Le jugement d'un modèle varie d'une exécution à l'autre : la fiche de tests repose sur une passe par test, sur une seule machine (Windows 11) ; la constance reste à mesurer.
- Les mesures datent du 13/10/2026 (Claude Code 2.1.296) ; une autre version peut se comporter autrement, en particulier pour les permissions.
- Les permissions sont une barrière, pas une sandbox : une commande qu'aucune règle ne couvre retombe sur la demande d'autorisation, que l'humain doit lire avant d'accepter.
- En mode non interactif (`claude -p`), une action qui demanderait une autorisation est refusée d'office ; en session normale, c'est l'humain qui décide.

## Correspondance avec le cours

| Élément du cours | Dans ce dossier |
|---|---|
| Skill : name, description quoi · quand · quand pas, étapes, format, règles, exemples dont un refusé, script | `.claude/skills/foot-go/` |
| Few-shot : 3 à 5 exemples variés, séparés des instructions | `references/` : trois niveaux différents + un cas refusé, lus à la demande |
| CLAUDE.md : Mission · Droits · Interdits · Méthode · Arrêt | `CLAUDE.md` |
| settings.json : mode standard, allow minimal, deny | `.claude/settings.json` |
| Condition d'arrêt + maxTurns | « Quand s'arrêter » + `maxTurns` du vérificateur |
| Évaluateur-optimiseur sur Haiku, sans droit d'écriture | `.claude/agents/verificateur.md` |
| Déterministe dès qu'on peut | `check_prompt.py` : la forme n'est jamais estimée par le modèle |
