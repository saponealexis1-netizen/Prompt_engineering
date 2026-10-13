"""Tests du validateur de forme. Lancer depuis la racine : python -m unittest discover -s tests -v"""
import codecs
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "foot-go"
SCRIPT = SKILL / "scripts" / "check_prompt.py"
sys.path.insert(0, str(SCRIPT.parent))
from check_prompt import check  # noqa: E402


def read(path):
    return path.read_text(encoding="utf-8")


def ref(name):
    return read(SKILL / "references" / name)


class References(unittest.TestCase):
    def test_les_trois_references_sont_conformes_a_leur_niveau(self):
        for name, level in (("1_CIBLEE.md", "CIBLEE"), ("2_BORNEE.md", "BORNEE"), ("3_CRITIQUE.md", "CRITIQUE")):
            result = check(ref(name))
            self.assertEqual(result["erreurs"], [], name)
            self.assertEqual(result["niveau"], level, name)


class Structure(unittest.TestCase):
    def setUp(self):
        self.go = ref("2_BORNEE.md")

    def assertError(self, text, code):
        self.assertIn(code, check(text)["erreurs"])

    def test_stop_absent(self):
        self.assertError(re.sub(r"(?m)^\*\*STOP.*$", "", self.go), "STOP_MISSING")

    def test_titre_de_niveau_3_ne_compte_pas(self):
        self.assertError(self.go.replace("## PURPOSE", "### PURPOSE"), "PURPOSE_MISSING")

    def test_sans_section_numerotee(self):
        self.assertError(re.sub(r"(?m)^## \d+\.[^\n]*$", "Texte libre.", self.go), "NUMBERED_SECTION_MISSING")

    def test_sans_final_return(self):
        self.assertError(self.go.replace("## FINAL RETURN", "## RETOUR"), "FINAL_RETURN_MISSING")

    def test_bornee_sans_absolute_boundary(self):
        self.assertError(self.go.replace("## ABSOLUTE BOUNDARY", "## LIMITES"), "ABSOLUTE_BOUNDARY_MISSING")

    def test_bornee_sans_require(self):
        self.assertError(re.sub(r"(?m)^Require:.*$", "", self.go), "REQUIRE_MISSING")

    def test_niveau_invalide(self):
        self.assertError(self.go.replace("**NIVEAU:** BORNÉE", "**NIVEAU:** SURPUISSANT"), "LEVEL_MISSING_OR_INVALID")

    def test_ciblee_trop_longue(self):
        self.assertError(ref("1_CIBLEE.md") + "\nmot" * 200, "TOO_LONG_FOR_CIBLEE")

    def test_variantes_acceptees_sans_accent_et_espace_francais(self):
        for variant in (self.go.replace("BORNÉE", "BORNEE"), self.go.replace("**NIVEAU:**", "**NIVEAU :**")):
            self.assertEqual(check(variant)["erreurs"], [])


class Critique(unittest.TestCase):
    def setUp(self):
        self.go = ref("3_CRITIQUE.md")

    def test_sans_section_de_controles(self):
        self.assertIn("CONTROLS_SECTION_MISSING", check(self.go.replace("## 3. CONTRÔLES", "## 3. ÉTAPES"))["erreurs"])

    def test_stop_dans_une_phrase_ne_compte_pas(self):
        go = re.sub(r"(?m)^\*\*STOP.*$", "", self.go)
        self.assertIn("STOP immédiat", go)
        self.assertIn("STOP_MISSING", check(go)["erreurs"])

    def test_un_seul_require_ne_suffit_pas(self):
        lines = self.go.splitlines()
        kept, seen = [], 0
        for line in lines:
            if line.startswith("Require:"):
                seen += 1
                if seen > 1:
                    continue
            kept.append(line)
        self.assertIn("REQUIRE_MISSING", check("\n".join(kept))["erreurs"])


class Securite(unittest.TestCase):
    def setUp(self):
        self.go = ref("2_BORNEE.md")

    def with_line(self, line):
        return self.go.replace("## FINAL RETURN", line + "\n\n## FINAL RETURN")

    def test_commande_push_detectee(self):
        result = check(self.with_line("Lancer `git push origin main` à la fin."))
        self.assertIn("DANGEROUS_COMMAND", result["erreurs"])

    def test_negation_non_signalee(self):
        self.assertEqual(check(self.with_line("Aucun `git push` ni `git merge`."))["erreurs"], [])

    def test_bloc_de_code_detecte(self):
        self.assertIn("DANGEROUS_COMMAND", check(self.with_line("```\nRemove-Item donnees -Recurse\n```"))["erreurs"])

    def test_identifiant_absent_de_la_demande(self):
        go = self.with_line("Partir du commit a1b2c3d.")
        self.assertIn("UNKNOWN_IDENTIFIER", check(go, "Contrôle des compositions.")["erreurs"])
        self.assertEqual(check(go, "Contrôle des compositions à partir du commit a1b2c3d.")["erreurs"], [])

    def test_demande_vide(self):
        self.assertIn("REQUEST_EMPTY", check(self.go, "   ")["erreurs"])


class Piege(unittest.TestCase):
    def test_le_go_piege_passe_le_script_qui_ne_juge_que_la_forme(self):
        # Volontaire : le GO piégé est bien formé ; seul le vérificateur peut voir qu'il trahit la demande.
        result = check(read(ROOT / "tests" / "piege" / "GO.md"), read(ROOT / "tests" / "piege" / "DEMANDE.md"))
        self.assertEqual(result["erreurs"], [])


class LigneDeCommande(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_sans_argument_code_2(self):
        self.assertEqual(self.run_cli().returncode, 2)

    def test_fichier_absent_code_1(self):
        proc = self.run_cli("absent.md")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("FILE_NOT_FOUND", proc.stdout)

    def test_demande_absente_code_1(self):
        proc = self.run_cli(str(SKILL / "references" / "2_BORNEE.md"), "demande_absente.md")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("REQUEST_EMPTY", proc.stdout)

    def test_fichier_avec_bom_accepte(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "GO.md"
            path.write_bytes(codecs.BOM_UTF8 + ref("2_BORNEE.md").encode("utf-8"))
            proc = self.run_cli(str(path))
        self.assertEqual(proc.returncode, 0, proc.stdout)


if __name__ == "__main__":
    unittest.main()
