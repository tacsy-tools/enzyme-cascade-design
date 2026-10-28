"""Check DG/kinetic-table association and rejection of incomplete stale inputs."""

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from dg_kinetics import assemble, initialize, signature

HERE = Path(__file__).resolve().parents[1]


class DgKineticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        original = json.loads(
            (HERE / "examples/9mec/kinetic-reference.json").read_text()
        )
        self.original = original
        native = deepcopy(original)
        native["species"] = {
            ("HTD" if s == "Htd" else s): {"carbon": 0} for s in original["species"]
        }
        for i, r in enumerate(native["reactions"]):
            r["id"] = f"dg{i + 39}"
            for side in ("reactants", "products"):
                r[side] = {("HTD" if s == "Htd" else s): n for s, n in r[side].items()}
            del r["kinetics"]
        self.network = self.root / "network.json"
        self.network.write_text(json.dumps(native))
        self.source = self.root / "original.json"
        # Import must not depend on matching reaction order or reaction IDs.
        original["reactions"].reverse()
        self.source.write_text(json.dumps(original))
        self.tables = self.root / "tables"

    def test_import_associates_by_stoichiometry_and_normalizes_alias(self):
        initialize(self.network, self.tables, self.source)
        model = assemble(self.network, self.tables)
        self.assertEqual(len(model["reactions"]), 19)
        by_signature = {signature(r): r for r in self.original["reactions"]}
        for r in model["reactions"]:
            old = by_signature[signature(r)]["kinetics"]
            self.assertEqual(r["kinetics"]["constants"], old["constants"])
            self.assertEqual(r["kinetics"]["type"], old["type"])
        self.assertIn("HTD", model["species"])
        self.assertNotIn("Htd", model["species"])
        self.assertEqual(
            model["species"]["HTD"]["initial"],
            self.original["species"]["Htd"]["initial"],
        )

    def test_unknown_kinetics_are_not_invented(self):
        initialize(self.network, self.tables)
        with self.assertRaisesRegex(ValueError, "Missing initial concentration"):
            assemble(self.network, self.tables)

    def test_changed_network_requires_review(self):
        initialize(self.network, self.tables, self.source)
        model = json.loads(self.network.read_text())
        model["reactions"][0]["reactants"]["Dhq"] = 2
        self.network.write_text(json.dumps(model))
        with self.assertRaisesRegex(ValueError, "Network changed"):
            assemble(self.network, self.tables)

    def test_ambiguous_kinetics_are_rejected_and_existing_tables_preserved(self):
        initialize(self.network, self.tables, self.source)
        saved = (self.tables / "kinetics.csv").read_bytes()
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            initialize(self.network, self.tables, self.source)
        self.assertEqual((self.tables / "kinetics.csv").read_bytes(), saved)
        original = json.loads(self.source.read_text())
        original["reactions"].append(deepcopy(original["reactions"][0]))
        self.source.write_text(json.dumps(original))
        with self.assertRaisesRegex(ValueError, "Ambiguous kinetics import"):
            initialize(self.network, self.root / "ambiguous", self.source)


if __name__ == "__main__":
    unittest.main()
