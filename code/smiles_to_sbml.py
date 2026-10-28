#!/usr/bin/env python3
"""Convert directed reaction SMILES (reactants>>products [id]) to SBML L3V2.

Repeated dot-separated components become stoichiometric coefficients. SMILES
are species identifiers, not a source of kinetic laws or flux constraints.
"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

S_ID = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*$")
ANNOTATION_NS = "https://tacsy.eu/ns/network-export/v1"


def read_reactions(path):
    reactions = []
    identifiers = set()
    for number, raw in enumerate(Path(path).read_text().splitlines(), 1):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        fields = raw.split()
        if len(fields) > 2:
            raise ValueError(f"Line {number}: expected reaction SMILES and optional ID")
        equation = fields[0]
        if equation.count(">") != 2 or ">>" not in equation:
            raise ValueError(
                f"Line {number}: expected reactants>>products without agents"
            )
        left, right = equation.split(">>")
        if not left and not right:
            raise ValueError(f"Line {number}: empty reaction")
        sides = [side.split(".") if side else [] for side in (left, right)]
        if any(not token for side in sides for token in side):
            raise ValueError(f"Line {number}: empty molecule component")
        identifier = fields[1] if len(fields) == 2 else f"r{len(reactions) + 1}"
        if not S_ID.fullmatch(identifier) or identifier in identifiers:
            raise ValueError(
                f"Line {number}: invalid or duplicate reaction ID {identifier!r}"
            )
        identifiers.add(identifier)
        reactions.append(
            {
                "id": identifier,
                "equation": equation,
                "reactants": Counter(sides[0]),
                "products": Counter(sides[1]),
            }
        )
    if not reactions:
        raise ValueError("No reactions found")
    return reactions


def checked(result, action):
    # libSBML setters return 0 on success.
    if result != 0:
        raise ValueError(f"libSBML failed to {action}: return code {result}")


def annotate(element, tag, data):
    xml = ET.Element(f"{{{ANNOTATION_NS}}}{tag}")
    for key, value in data.items():
        child = ET.SubElement(xml, f"{{{ANNOTATION_NS}}}{key}")
        child.text = (
            value if isinstance(value, str) else json.dumps(value, sort_keys=True)
        )
    checked(
        element.setAnnotation(ET.tostring(xml, encoding="unicode")), "set annotation"
    )


def build_document(reactions, metadata=None, model_id="tacsy_3hp"):
    import libsbml

    if not S_ID.fullmatch(model_id):
        raise ValueError(f"Invalid model ID: {model_id!r}")
    metadata = metadata or {}
    if metadata and metadata.get("format") != "tacsy-reaction-network-v1":
        raise ValueError("Unsupported metadata format")
    reaction_ids = {r["id"] for r in reactions}
    if metadata:
        species = metadata["species"]
    else:
        smiles = sorted(
            {
                s
                for r in reactions
                for side in ("reactants", "products")
                for s in r[side]
            }
        )
        species = [
            {"id": f"s{i}", "name": s, "smiles": s} for i, s in enumerate(smiles)
        ]
    by_smiles = {s["smiles"]: s for s in species}
    species_ids = {s["id"] for s in species}
    if len(by_smiles) != len(species) or len(species_ids) != len(species):
        raise ValueError("Duplicate species ID or SMILES in metadata")
    if any(not S_ID.fullmatch(s) for s in species_ids):
        raise ValueError("Invalid species ID in metadata")
    if reaction_ids & species_ids:
        raise ValueError("Species and reaction IDs overlap")
    used_ids = species_ids | reaction_ids | {model_id}
    compartment_id = "compartment"
    while compartment_id in used_ids:
        compartment_id += "_"

    metadata_reactions = {r["id"]: r for r in metadata.get("reactions", [])}
    if metadata and (
        set(metadata_reactions) != reaction_ids
        or len(metadata_reactions) != len(metadata["reactions"])
    ):
        raise ValueError("Reaction IDs differ between SMILES and metadata")

    document = libsbml.SBMLDocument(3, 2)
    model = document.createModel()
    checked(model.setId(model_id), "set model ID")
    checked(model.setName("TACsy reaction network"), "set model name")
    for setter, value in [
        (model.setSubstanceUnits, "mole"),
        (model.setExtentUnits, "mole"),
        (model.setTimeUnits, "second"),
    ]:
        checked(setter(value), "set model units")
    annotate(
        model,
        "network",
        {
            "kind": "stoichiometric network; no kinetic laws or flux constraints",
            **{
                key: metadata[key]
                for key in (
                    "expansion_rounds",
                    "mod_version",
                    "max_explicit_carbon_atoms",
                    "abstract_atom_legend",
                )
                if key in metadata
            },
        },
    )
    compartment = model.createCompartment()
    for setter, value in [
        (compartment.setId, compartment_id),
        (compartment.setConstant, True),
        (compartment.setSpatialDimensions, 3),
        (compartment.setSize, 1),
        (compartment.setUnits, "litre"),
    ]:
        checked(setter(value), "set compartment attribute")
    for item in species:
        entity = model.createSpecies()
        for setter, value in [
            (entity.setId, item["id"]),
            (entity.setName, item.get("name", item["smiles"])),
            (entity.setCompartment, compartment_id),
            (entity.setConstant, False),
            (entity.setBoundaryCondition, False),
            (entity.setHasOnlySubstanceUnits, True),
            (entity.setSubstanceUnits, "mole"),
        ]:
            checked(setter(value), "set species attribute")
        annotate(
            entity,
            "species",
            {k: v for k, v in item.items() if k not in ("id", "name")},
        )
    for item in reactions:
        reaction = model.createReaction()
        checked(reaction.setId(item["id"]), "set reaction ID")
        checked(reaction.setReversible(False), "set reaction direction")
        exact = metadata_reactions.get(item["id"])
        if exact and exact["reaction_smiles"] != item["equation"]:
            raise ValueError(f"SMILES differs from metadata for {item['id']}")
        for side, create in [
            ("reactants", reaction.createReactant),
            ("products", reaction.createProduct),
        ]:
            counts = {}
            for smiles, coefficient in item[side].items():
                if smiles not in by_smiles:
                    raise ValueError(f"Species missing from metadata: {smiles}")
                species_id = by_smiles[smiles]["id"]
                counts[species_id] = coefficient
                reference = create()
                checked(reference.setSpecies(species_id), "set species reference")
                checked(reference.setStoichiometry(coefficient), "set stoichiometry")
                checked(reference.setConstant(True), "set constant stoichiometry")
            if exact and counts != exact[side]:
                raise ValueError(
                    f"Stoichiometry differs from metadata for {item['id']}"
                )
        annotate(reaction, "derivation", exact or {"reaction_smiles": item["equation"]})
    return document


def validate(document):
    document.checkConsistency()
    diagnostics = [
        {
            "severity": document.getError(i).getSeverityAsString(),
            "id": document.getError(i).getErrorId(),
            "message": document.getError(i).getMessage().strip(),
        }
        for i in range(document.getNumErrors())
    ]
    errors = [d for d in diagnostics if d["severity"] in ("Error", "Fatal")]
    if errors:
        raise ValueError("Invalid SBML: " + json.dumps(errors))
    return diagnostics


def convert(source, target, metadata_path=None, model_id="tacsy_3hp"):
    import libsbml

    metadata = json.loads(Path(metadata_path).read_text()) if metadata_path else None
    document = build_document(read_reactions(source), metadata, model_id)
    validate(document)
    # Validate the serialized document too, before committing the output file.
    serialized = libsbml.writeSBMLToString(document)
    reopened = libsbml.readSBMLFromString(serialized)
    diagnostics = validate(reopened)
    model = reopened.getModel()
    report = {
        "species": model.getNumSpecies(),
        "reactions": model.getNumReactions(),
        "sbml_level": 3,
        "sbml_version": 2,
        "errors": 0,
        "diagnostics": diagnostics,
        "libsbml_version": libsbml.getLibSBMLDottedVersion(),
    }
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(serialized)
    target.with_suffix(".validation.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source", type=Path, help="reaction SMILES, one reaction per line"
    )
    parser.add_argument("target", type=Path, help="output SBML file")
    parser.add_argument(
        "--metadata", type=Path, help="network.json from export_network.py"
    )
    parser.add_argument("--model-id", default="tacsy_3hp")
    args = parser.parse_args()
    try:
        report = convert(args.source, args.target, args.metadata, args.model_id)
    except ImportError:
        parser.exit(
            1,
            "Install the converter dependency: python3 -m pip install python-libsbml\n",
        )
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"{error}\n")
    print(
        f"SBML: {report['species']} species, {report['reactions']} reactions; "
        f"0 validation errors, {len(report['diagnostics'])} diagnostics. File: {args.target}"
    )


if __name__ == "__main__":
    main()
