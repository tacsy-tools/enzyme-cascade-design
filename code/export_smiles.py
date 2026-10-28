#!/usr/bin/env python3
"""Expand the 3HP MØD network and export reaction SMILES plus provenance."""

import json
import re
from collections import Counter


def export_network(
    dg,
    output,
    *,
    rounds,
    rules,
    mod_version,
    invalid_atom_id,
    max_explicit_carbon_atoms=None,
):
    vertices = sorted(dg.vertices, key=lambda v: v.id)
    # Isotopically labelled dummy atoms are valid SMILES. Their legend retains
    # abstract labels without inventing full chemical structures for cofactors.
    abstract_labels = sorted(
        {
            v.stringLabel
            for node in vertices
            for v in node.graph.vertices
            if v.atomId == invalid_atom_id
        }
    )
    dummy_atoms = {label: f"[{i}*]" for i, label in enumerate(abstract_labels, 1)}

    def standard_smiles(value):
        return re.sub(
            r"\[([^\[\]]+)\]", lambda m: dummy_atoms.get(m.group(1), m.group(0)), value
        )

    species = []
    for node in vertices:
        graph = node.graph
        original = graph.smiles
        species.append(
            {
                "id": f"s{node.id}",
                "dg_vertex_id": node.id,
                "name": graph.name,
                "smiles": standard_smiles(original),
                "mod_smiles": original,
                "graph_dfs": graph.graphDFS,
                "explicit_carbon_atoms": graph.vLabelCount("C"),
                "abstract_labels": sorted(
                    {
                        v.stringLabel
                        for v in graph.vertices
                        if v.atomId == invalid_atom_id
                    }
                ),
            }
        )
    by_id = {s["id"]: s for s in species}
    if len({s["smiles"] for s in species}) != len(species):
        raise ValueError("Distinct DG species share SMILES; cannot export losslessly.")

    derivations = []
    for edge in sorted(dg.edges, key=lambda e: e.id):
        sources = [f"s{v.id}" for v in edge.sources]
        targets = [f"s{v.id}" for v in edge.targets]

        def equation(key):
            return (
                ".".join(by_id[s][key] for s in sources)
                + ">>"
                + ".".join(by_id[s][key] for s in targets)
            )

        derivations.append(
            {
                "id": f"r{edge.id}",
                "dg_edge_id": edge.id,
                "reactants": dict(Counter(sources)),
                "products": dict(Counter(targets)),
                "rules": sorted(r.name for r in edge.rules),
                "rule_ids": sorted(r.id for r in edge.rules),
                "reaction_smiles": equation("smiles"),
                "mod_reaction_smiles": equation("mod_smiles"),
            }
        )
    data = {
        "format": "tacsy-reaction-network-v1",
        "expansion_rounds": rounds,
        "mod_version": str(mod_version),
        "rules": rules,
        "abstract_atom_legend": dummy_atoms,
        "species": species,
        "reactions": derivations,
    }
    if max_explicit_carbon_atoms is not None:
        data["max_explicit_carbon_atoms"] = max_explicit_carbon_atoms
    output.mkdir(parents=True, exist_ok=True)
    (output / "network.json").write_text(json.dumps(data, indent=2) + "\n")
    for filename, key in [
        ("reactions.smi", "reaction_smiles"),
        ("reactions.mod.smi", "mod_reaction_smiles"),
    ]:
        (output / filename).write_text(
            "".join(f"{r[key]}\t{r['id']}\n" for r in derivations)
        )
    print(
        f"Exported {len(species)} species and {len(derivations)} reactions to {output}"
    )
    if dummy_atoms:
        print("Abstract cofactor labels represented by dummy atoms:", dummy_atoms)
    return data
