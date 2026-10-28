"""Reject ambiguous chemistry, stale inputs and boundary shortcuts."""

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import HERE, load, validate_network
from network import from_sbml, normalize
from scan import prepare


class InterfaceTests(unittest.TestCase):
    def test_all_shipped_networks_are_carbon_balanced(self):
        for path in ["examples/3hp/network.json", "examples/9mec/network/network.json"]:
            validate_network(load(HERE / path))

    def test_missing_carbon_is_an_error(self):
        network = load(HERE / "examples/3hp/network.json")
        del network["species"]["PYR"]["carbon"]
        with self.assertRaisesRegex(ValueError, "Every species"):
            validate_network(network)

    def test_sbml_direction_and_bounds_are_not_silently_ignored(self):
        source = HERE / "examples/3hp/network.sbml"
        ns = {"s": "http://www.sbml.org/sbml/level3/version2/core"}
        root = ET.parse(source)
        model = root.find("s:model", ns)
        reaction = model.find("s:listOfReactions/s:reaction", ns)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.sbml"
            reaction.set("reversible", "true")
            root.write(path)
            with self.assertRaisesRegex(ValueError, "Reversible"):
                from_sbml(path)
            reaction.set("reversible", "false")
            core = "{" + ns["s"] + "}"
            fbc = "{http://www.sbml.org/sbml/level3/version2/fbc}"
            params = ET.SubElement(model, core + "listOfParameters")
            ET.SubElement(params, core + "parameter", id="lower", value="0")
            ET.SubElement(params, core + "parameter", id="upper", value="0")
            reaction.set(fbc + "lowerFluxBound", "lower")
            reaction.set(fbc + "upperFluxBound", "upper")
            root.write(path)
            data = normalize(
                from_sbml(path),
                load(HERE / "examples/3hp/cofactor-carbon.json"),
                "test",
            )
            self.assertEqual(data["reactions"][0]["bounds"], [0, 0])
            params[0].set("value", "-1")
            root.write(path)
            with self.assertRaisesRegex(ValueError, "Reverse flux"):
                from_sbml(path)

    def test_unknown_enzyme_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "Unknown enzyme"):
                prepare(
                    HERE / "examples/9mec/model.json",
                    Path(temp) / "run",
                    ["Va"],
                    variants=[{"case": "bad", "factors": {"TYPO": 2}}],
                )


if __name__ == "__main__":
    unittest.main()
