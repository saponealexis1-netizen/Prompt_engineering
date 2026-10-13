"""Contrôles de la configuration de l'agent : permissions, sous-agent, skill, CLAUDE.md."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERMISSIONS = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))["permissions"]
SCRIPT_CMD = "python .claude/skills/foot-go/scripts/check_prompt.py *"


def frontmatter(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    end = lines.index("---", 1)
    return dict(line.split(": ", 1) for line in lines[1:end])


class Permissions(unittest.TestCase):
    def test_mode_standard(self):
        self.assertEqual(PERMISSIONS["defaultMode"], "default")

    def test_seuls_le_script_et_les_livrables_sont_autorises_sans_demander(self):
        expected = [f"Bash({SCRIPT_CMD})", f"PowerShell({SCRIPT_CMD})", "Edit(./livrables/**)"]
        self.assertEqual(sorted(PERMISSIONS["allow"]), sorted(expected))

    def test_commandes_dangereuses_bloquees_en_bash_et_en_powershell(self):
        for cmd in ("git push *", "git push", "git merge *", "rm *", "curl *", "wget *"):
            self.assertIn(f"Bash({cmd})", PERMISSIONS["deny"])
            self.assertIn(f"PowerShell({cmd})", PERMISSIONS["deny"])
        for cmd in ("Remove-Item *", "del *", "Invoke-WebRequest *", "Invoke-RestMethod *", "iwr *", "irm *"):
            self.assertIn(f"PowerShell({cmd})", PERMISSIONS["deny"])

    def test_secrets_donnees_et_configuration_proteges(self):
        for rule in ("Read(./.env)", "Read(./.env.*)", "Read(./data/**)", "Read(./tests/**)", "Edit(./data/**)",
                     "Edit(./.claude/**)", "Edit(./tests/**)", "Edit(./CLAUDE.md)", "Edit(./README.md)",
                     "Edit(./.gitignore)", "WebFetch", "WebSearch"):
            self.assertIn(rule, PERMISSIONS["deny"])


class Agent(unittest.TestCase):
    def test_verificateur_en_lecture_seule_sur_haiku(self):
        meta = frontmatter(ROOT / ".claude" / "agents" / "verificateur.md")
        self.assertEqual(meta["tools"], "Read, Grep, Glob")
        self.assertEqual(meta["model"], "haiku")
        self.assertTrue(meta["maxTurns"].isdigit())

    def test_skill_nomme_comme_son_dossier_avec_quand_pas(self):
        meta = frontmatter(ROOT / ".claude" / "skills" / "foot-go" / "SKILL.md")
        self.assertEqual(meta["name"], "foot-go")
        self.assertIn("Ne pas utiliser", meta["description"])
        self.assertLessEqual(len(meta["description"]), 1024)

    def test_claude_md_a_les_cinq_sections_du_cours(self):
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        for section in ("## Mission", "## Droits", "## Interdits", "## Méthode", "## Quand s'arrêter"):
            self.assertIn(section, text)


if __name__ == "__main__":
    unittest.main()
