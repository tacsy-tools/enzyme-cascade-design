"""Create small editable kinetic tables for a generated DG network; build ODE input.

Stoichiometry stays in the generated network.json. People edit kinetics.csv
and initial.csv, not a second copy of the reaction network. Existing Julia
assignments can be imported by exact stoichiometric signature, never by order.
"""

import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from generate_julia import validate

HERE = Path(__file__).resolve().parent
ALIASES = {"Htd": "HTD"}


def signature(reaction):
    return tuple(
        tuple(sorted((ALIASES.get(s, s), n) for s, n in reaction[side].items()))
        for side in ("reactants", "products")
    )


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_table(path, fields, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def initialize(network_path, directory, import_path=None):
    network = json.loads(network_path.read_text())
    library = json.loads((HERE / "examples/9mec/kinetic-reference.json").read_text())
    original = json.loads(import_path.read_text()) if import_path else None
    laws = (original or library)["rate_laws"]
    candidates = {}
    if original:
        for r in original["reactions"]:
            candidates.setdefault(signature(r), []).append(r)
    arguments = list(
        dict.fromkeys(a for law in laws.values() for a in law["arguments"])
    )
    rows = []
    for reaction in network["reactions"]:
        matches = candidates.get(signature(reaction), [])
        if len(matches) > 1:
            raise ValueError(f"Ambiguous kinetics import: {reaction['id']}")
        row = dict.fromkeys(
            ["reaction", "type", "mode", "imported_from", *arguments], ""
        )
        row["reaction"] = reaction["id"]
        if matches:
            source = matches[0]
            kinetics = source["kinetics"]
            row.update(
                type=kinetics["type"],
                mode=kinetics["mode"],
                imported_from=source.get("enzyme", source["id"]),
            )
            row.update(kinetics["constants"])
            row.update({a: ALIASES.get(s, s) for a, s in kinetics["species"].items()})
        rows.append(row)
    initial = (
        {ALIASES.get(s, s): info["initial"] for s, info in original["species"].items()}
        if original
        else {}
    )
    if directory.exists() and any(directory.iterdir()):
        raise ValueError(f"Refusing to overwrite existing kinetic tables: {directory}")
    directory.mkdir(parents=True, exist_ok=True)
    write_table(
        directory / "kinetics.csv",
        ["reaction", "type", "mode", "imported_from", *arguments],
        rows,
    )
    write_table(
        directory / "initial.csv",
        ["species", "initial"],
        [{"species": s, "initial": initial.get(s, "")} for s in network["species"]],
    )
    settings = {
        "schema": "dg-kinetics-v1",
        "network_sha256": digest(network_path),
        "time": original["time"]
        if original
        else {"span": [0.0, 1000.0], "save_points": 201},
        "units": "UNCONFIRMED: specify concentration and time units before biological interpretation",
        "rate_laws": laws,
        "species_aliases": ALIASES,
        "imported_kinetics_sha256": digest(import_path) if import_path else None,
        "imported_provenance": original.get("provenance") if original else None,
    }
    (directory / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    print(
        f"Created {len(rows)} reaction rows, {len(initial)} imported initial values in {directory}"
    )


def assemble(network_path, directory):
    network = json.loads(network_path.read_text())
    settings = json.loads((directory / "settings.json").read_text())
    if settings["network_sha256"] != digest(network_path):
        raise ValueError(
            "Network changed: regenerate and review the kinetic tables before reusing assignments"
        )
    with (directory / "initial.csv").open() as handle:
        initial_rows = list(csv.DictReader(handle))
    initial = {}
    for row in initial_rows:
        s = row["species"]
        if s in initial:
            raise ValueError(f"Duplicate initial concentration: {s}")
        if not row["initial"]:
            raise ValueError(f"Missing initial concentration: {s}")
        initial[s] = float(row["initial"])
    if set(initial) != set(network["species"]):
        raise ValueError("Initial concentrations must cover exactly the DG species")
    with (directory / "kinetics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assignments = {}
    for row in rows:
        name = row["reaction"]
        if name in assignments:
            raise ValueError(f"Duplicate kinetic assignment: {name}")
        kind = row["type"]
        if kind not in settings["rate_laws"]:
            raise ValueError(f"Missing/unknown rate-law type for {name}: {kind!r}")
        law = settings["rate_laws"][kind]
        kin = {"type": kind, "mode": row["mode"], "species": {}, "constants": {}}
        for argument in law["arguments"]:
            value = row.get(argument, "")
            if not value:
                raise ValueError(f"Missing kinetic argument: {name}.{argument}")
            try:
                kin["constants"][argument] = float(value)
            except ValueError:
                if value not in initial:
                    raise ValueError(
                        f"Unknown species or invalid number: {name}.{argument}={value}"
                    )
                kin["species"][argument] = value
        unused = {
            a: row.get(a)
            for definition in settings["rate_laws"].values()
            for a in definition["arguments"]
            if a not in law["arguments"] and row.get(a)
        }
        if unused:
            raise ValueError(f"Arguments not used by {kind} in {name}: {unused}")
        assignments[name] = kin
    if set(assignments) != {r["id"] for r in network["reactions"]}:
        raise ValueError("Kinetic assignments must cover exactly the DG reactions")
    model = {
        "name": network["name"],
        "time": settings["time"],
        "rate_laws": settings["rate_laws"],
        "species": {
            s: {**network["species"][s], "initial": initial[s]}
            for s in network["species"]
        },
        "reactions": [
            {
                **deepcopy(r),
                "enzyme": next(
                    row["imported_from"] or r["id"]
                    for row in rows
                    if row["reaction"] == r["id"]
                ),
                "kinetics": assignments[r["id"]],
            }
            for r in network["reactions"]
        ],
        "provenance": {
            "network_sha256": digest(network_path),
            "units": settings["units"],
            "kinetics_files": {
                p.name: digest(p) for p in sorted(directory.iterdir()) if p.is_file()
            },
            "imported_kinetics_sha256": settings["imported_kinetics_sha256"],
        },
    }
    validate(model)
    return model
