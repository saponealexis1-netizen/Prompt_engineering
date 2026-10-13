"""Contrôle déterministe de la FORME d'un prompt GO (sans réseau ni dépendance).

Usage : python .claude/skills/foot-go/scripts/check_prompt.py GO.md [DEMANDE.md]
Code de sortie : 0 = forme conforme, 1 = non conforme, 2 = mauvais usage.

Le script juge la forme. Le fond (la demande est-elle bien traitée ?) revient au
sous-agent vérificateur. La détection des commandes dangereuses est une heuristique :
une commande entre backticks sur une ligne sans négation (aucun, jamais, interdit, pas).
"""
from pathlib import Path
import json
import re
import sys

BUDGET = {"CIBLEE": 250, "BORNEE": 600, "CRITIQUE": 1000}
REQUIRE_MIN = {"CIBLEE": 0, "BORNEE": 1, "CRITIQUE": 2}
FIXED = ("PURPOSE", "ABSOLUTE BOUNDARY", "FINAL RETURN")

TITLE_RE = re.compile(r"^GO\s*[—–-]\s*\S")
LEVEL_RE = re.compile(r"^\*\*NIVEAU\s*:\*\*\s*(CIBL[EÉ]E|BORN[EÉ]E|CRITIQUE)\s*$", re.M)
HEADING_RE = re.compile(r"^##[ \t]+(?:(\d+)\.[ \t]*)?(\S[^\n]*?)[ \t]*$", re.M)
REQUIRE_RE = re.compile(r"^[ \t]*(?:[-*][ \t]*)?Require[ \t]*:[ \t]*\S", re.M)
STOP_RE = re.compile(r"^[ \t]*(?:\*\*)?[ \t]*STOP\b", re.M)
CONTROL_RE = re.compile(r"CONTR[OÔ]LE|V[EÉ]RIFICATION", re.I)
DANGER_RE = re.compile(r"git\s+push|git\s+merge|git\s+reset\s+--hard|\brm\s+-|Remove-Item|\bdel\s"
                       r"|\bcurl\b|\bwget\b|Invoke-WebRequest|Invoke-RestMethod|--force", re.I)
NEGATION_RE = re.compile(r"\b(?:aucun|aucune|jamais|interdit|interdite|interdits|interdites|pas)\b", re.I)
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
HEX_ID_RE = re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")


def dangerous_commands(text):
    """Commandes d'exécution risquées citées comme code, hors phrase de négation."""
    found, in_fence = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if NEGATION_RE.search(line):
            continue
        spans = [line] if in_fence else INLINE_CODE_RE.findall(line)
        for span in spans:
            found += [m.group(0) for m in DANGER_RE.finditer(span)]
    return found


def unknown_identifiers(text, request):
    """Identifiants hexadécimaux (commit, empreinte) cités dans le GO mais absents de la demande."""
    known = set(HEX_ID_RE.findall(request.lower()))
    return sorted({h for h in HEX_ID_RE.findall(text.lower()) if h not in known})


def check(content, request=None):
    text = content.lstrip(chr(0xFEFF))
    errors = []
    first = next((line for line in text.splitlines() if line.strip()), "")
    if not TITLE_RE.match(first):
        errors.append("GO_TITLE_MISSING")

    m = LEVEL_RE.search(text)
    level = m.group(1).replace("É", "E") if m else None
    if level is None:
        errors.append("LEVEL_MISSING_OR_INVALID")

    words = len(text.split())
    if level and words > BUDGET[level]:
        errors.append("TOO_LONG_FOR_" + level)

    headings = [(num, title.upper()) for num, title in HEADING_RE.findall(text)]
    titles = {title for _, title in headings}
    numbered = [title for num, title in headings if num and title not in FIXED]
    if "PURPOSE" not in titles:
        errors.append("PURPOSE_MISSING")
    if not numbered:
        errors.append("NUMBERED_SECTION_MISSING")
    if "FINAL RETURN" not in titles:
        errors.append("FINAL_RETURN_MISSING")
    if not STOP_RE.search(text):
        errors.append("STOP_MISSING")

    requires = len(REQUIRE_RE.findall(text))
    if level in ("BORNEE", "CRITIQUE") and "ABSOLUTE BOUNDARY" not in titles:
        errors.append("ABSOLUTE_BOUNDARY_MISSING")
    if level and requires < REQUIRE_MIN[level]:
        errors.append("REQUIRE_MISSING")
    if level == "CRITIQUE" and not any(CONTROL_RE.search(title) for title in numbered):
        errors.append("CONTROLS_SECTION_MISSING")

    danger = dangerous_commands(text)
    if danger:
        errors.append("DANGEROUS_COMMAND")

    unknown = []
    if request is not None:
        if not request.strip():
            errors.append("REQUEST_EMPTY")
        else:
            unknown = unknown_identifiers(text, request)
            if unknown:
                errors.append("UNKNOWN_IDENTIFIER")

    return {"status": "CONFORME_STRUCTURE" if not errors else "NON_CONFORME_STRUCTURE",
            "niveau": level, "mots": words, "budget": BUDGET.get(level),
            "sections_numerotees": len(numbered), "require": requires,
            "commandes_dangereuses": danger, "identifiants_inconnus": unknown,
            "erreurs": errors}


def main(argv):
    if len(argv) not in (2, 3):
        print("Usage : python check_prompt.py GO.md [DEMANDE.md]", file=sys.stderr)
        return 2
    go = Path(argv[1])
    if not go.is_file():
        print(json.dumps({"status": "NON_CONFORME_STRUCTURE", "erreurs": ["FILE_NOT_FOUND"]}))
        return 1
    request = None
    if len(argv) == 3:
        req = Path(argv[2])
        request = req.read_text(encoding="utf-8-sig") if req.is_file() else ""
    result = check(go.read_text(encoding="utf-8-sig"), request)
    print(json.dumps(result, indent=2))
    return 0 if not result["erreurs"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
