"""Build a bundled MØD example, with native DG, reaction SMILES, SBML and JSON."""

import argparse
import os
import re
import runpy
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from common import HERE, digest, load, save, validate_network


def normalize(metadata, groups, name):
    names = {s["id"]: s["name"] for s in metadata["species"]}
    if len(set(names.values())) != len(names):
        raise ValueError("Non-unique compound names; supply explicit aliases")
    species = {}
    for s in metadata["species"]:
        unknown = set(s.get("abstract_labels", [])) - set(groups)
        if unknown:
            raise ValueError(f"Unknown abbreviated groups: {unknown}")
        carbon = s["explicit_carbon_atoms"] + sum(
            s["graph_dfs"].count(f"[{label}]") * groups[label]["carbon"]
            for label in s.get("abstract_labels", [])
        )
        species[s["name"]] = {**s, "carbon": carbon}
    reactions = [
        {
            **r,
            **{
                side: {names[s]: n for s, n in r[side].items()}
                for side in ("reactants", "products")
            },
        }
        for r in metadata["reactions"]
    ]
    network = {
        "schema": "tacsy-design-network-v1",
        "name": name,
        "species": species,
        "reactions": reactions,
        "provenance": {
            "mod_version": metadata.get("mod_version"),
            "expansion_rounds": metadata.get("expansion_rounds"),
            "carbon_groups": groups,
        },
    }
    validate_network(network)
    return network


def build(case, output, rounds=7):
    import mod

    from export_smiles import export_network
    from smiles_to_sbml import convert

    source = HERE / "examples" / case / "source"
    namespace = dict(vars(mod), mod=mod, os=os, render=False, expansion_rounds=rounds)
    previous = Path.cwd()

    def include(filename):
        path = source / "Mod" / filename
        exec(compile(path.read_text(), str(path), "exec"), namespace)

    namespace["include"] = include
    try:
        if case == "9mec":
            os.chdir(source / "Mod")
            path = source / "Mod/dg.py"
            text = re.split(r"(?m)^dg\.print\(\)", path.read_text(), maxsplit=1)[0]
            exec(compile(text, str(path), "exec"), namespace)
        else:
            os.chdir(source)
            for name in ["3HP-grammar.py", "3HP-dg.py"]:
                namespace = runpy.run_path(str(source / name), init_globals=namespace)
    finally:
        os.chdir(previous)
    output.mkdir(parents=True, exist_ok=True)
    dg = namespace["dg"]
    dg.dump(str(output / "network.dg"))
    metadata = export_network(
        dg,
        output,
        rounds=rounds if case == "3hp" else None,
        rules=[],
        mod_version=mod.version(),
        invalid_atom_id=mod.AtomIds.Invalid,
        max_explicit_carbon_atoms=5 if case == "3hp" else None,
    )
    # Preserve original export metadata separately from the common query format.
    (output / "network.json").rename(output / "export-network.json")
    network = normalize(
        metadata, load(HERE / "examples" / case / "cofactor-carbon.json"), case
    )
    network["provenance"]["source_files"] = {
        str(p.relative_to(source)): digest(p)
        for p in sorted(source.rglob("*"))
        if p.is_file()
    }
    network["provenance"]["native_dg_sha256"] = digest(output / "network.dg")
    save(output / "network.json", network)
    convert(
        output / "reactions.smi",
        output / "network.sbml",
        output / "export-network.json",
        f"tacsy_{case}",
    )
    reopened = mod.DG.load([], [], str(output / "network.dg"))
    signature = lambda graph: sorted(
        (
            tuple(sorted(Counter(v.graph.name for v in e.sources).items())),
            tuple(sorted(Counter(v.graph.name for v in e.targets).items())),
        )
        for e in graph.edges
    )
    assert signature(dg) == signature(reopened)
    save(
        output / "validation.json",
        {
            "species": len(network["species"]),
            "reactions": len(network["reactions"]),
            "carbon_balanced": True,
            "native_reload_matches": True,
        },
    )
    print("Saved native DG, SMILES, SBML and annotated JSON:", output)


def from_sbml(path):
    """Read this release's annotated SBML; fail closed on unsupported directions."""
    ns = {
        "s": "http://www.sbml.org/sbml/level3/version2/core",
        "t": "https://tacsy.eu/ns/network-export/v1",
    }
    root = ET.parse(path).getroot()
    model = root.find("s:model", ns)
    species = []
    for item in model.findall("s:listOfSpecies/s:species", ns):
        info = {"id": item.get("id"), "name": item.get("name")}
        for key in [
            "smiles",
            "mod_smiles",
            "graph_dfs",
            "explicit_carbon_atoms",
            "abstract_labels",
        ]:
            node = item.find(f".//t:{key}", ns)
            if node is None:
                raise ValueError(
                    "Import requires the annotated SBML supplied with this release"
                )
            info[key] = (
                __import__("json").loads(node.text)
                if key in ["explicit_carbon_atoms", "abstract_labels"]
                else node.text
            )
        species.append(info)
    fbc = "{http://www.sbml.org/sbml/level3/version1/fbc}"
    fbc2 = "{http://www.sbml.org/sbml/level3/version2/fbc}"
    parameters = {
        p.get("id"): float(p.get("value"))
        for p in model.findall("s:listOfParameters/s:parameter", ns)
    }
    reactions = []
    for item in model.findall("s:listOfReactions/s:reaction", ns):
        r = {"id": item.get("id")}
        for side, title in [("reactants", "Reactants"), ("products", "Products")]:
            r[side] = {}
            for ref in item.findall(f"s:listOf{title}/s:speciesReference", ns):
                n = float(ref.get("stoichiometry", "1"))
                if not n.is_integer() or n <= 0:
                    raise ValueError("Only positive integer stoichiometry is supported")
                s = ref.get("species")
                r[side][s] = r[side].get(s, 0) + int(n)
        lo = item.get(fbc2 + "lowerFluxBound") or item.get(fbc + "lowerFluxBound")
        hi = item.get(fbc2 + "upperFluxBound") or item.get(fbc + "upperFluxBound")
        if bool(lo) != bool(hi):
            raise ValueError("Both SBML flux bounds are required")
        if lo:
            r["bounds"] = [parameters[lo], parameters[hi]]
            if r["bounds"][0] < 0:
                raise ValueError(
                    "Reverse flux requires an explicitly directed representation"
                )
        elif item.get("reversible", "true") != "false":
            raise ValueError(
                "Reversible reaction needs an explicitly directed representation"
            )
        reactions.append(r)
    return {"species": species, "reactions": reactions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    b = subs.add_parser("build")
    b.add_argument("case", choices=["3hp", "9mec"])
    b.add_argument("--output", type=Path, required=True)
    b.add_argument("--rounds", type=int, default=7)
    c = subs.add_parser("check")
    c.add_argument("input", type=Path)
    s = subs.add_parser("from-sbml")
    s.add_argument("input", type=Path)
    s.add_argument("--case", choices=["3hp", "9mec"], required=True)
    s.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            if args.rounds < 1:
                raise ValueError("rounds must be positive")
            build(args.case, args.output.resolve(), args.rounds)
        elif args.command == "check":
            network = load(args.input)
            validate_network(network)
            print(
                f"{len(network['species'])} species, {len(network['reactions'])} carbon-balanced reactions"
            )
        else:
            network = normalize(
                from_sbml(args.input),
                load(HERE / "examples" / args.case / "cofactor-carbon.json"),
                args.case,
            )
            network["provenance"]["sbml_sha256"] = digest(args.input)
            save(args.output, network)
    except (ValueError, KeyError, OSError, ImportError) as exc:
        parser.exit(1, f"Cannot prepare network: {exc}\n")


if __name__ == "__main__":
    main()
