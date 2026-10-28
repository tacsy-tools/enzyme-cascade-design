"""Prepare one-at-a-time enzyme changes, a Cartesian grid or named variants."""

import argparse
import csv
import math
import subprocess
from itertools import product
from pathlib import Path

from common import HERE, digest, load, save
from generate_julia import generate, validate


def prepare(
    model_path, output, products, factors=None, vary=None, variants=None, pools=None
):
    model = load(model_path)
    validate(model)
    if not products or set(products) - set(model["species"]):
        raise ValueError("Unknown or empty product selection")
    mapping = {
        r["enzyme"]: r
        for r in model["reactions"]
        if "enzyme" in r and "E" in r["kinetics"]["constants"]
    }
    if len(mapping) != len(model["reactions"]):
        raise ValueError(
            "Distinct reaction-specific enzyme labels and E constants are required"
        )
    cases = [{"case": "baseline", "factors": {}}]
    if variants is not None:
        cases.extend(variants)
    elif vary is not None:
        names = list(vary)
        cases.extend(
            {
                "case": "__".join(f"{e}_{v:g}x" for e, v in zip(names, values)),
                "factors": dict(zip(names, values)),
            }
            for values in product(*vary.values())
            if any(v != 1 for v in values)
        )
    else:
        cases.extend(
            {"case": f"{e}_{v:g}x", "factors": {e: v}}
            for e in mapping
            for v in factors
            if v != 1
        )
    if len(cases) > 10001:
        raise ValueError("Limit the scan to 10000 changed cases")
    identifiers = set()
    for case in cases:
        if case["case"] in identifiers or any(
            x in case["case"] for x in [",", "\n", "\r"]
        ):
            raise ValueError(
                "Case names must be unique and contain no commas or newlines"
            )
        identifiers.add(case["case"])
        if set(case["factors"]) - set(mapping):
            raise ValueError("Unknown enzyme in variants")
        if any(
            isinstance(v, bool)
            or not isinstance(v, (int, float))
            or not math.isfinite(v)
            or v <= 0
            for v in case["factors"].values()
        ):
            raise ValueError("Factors must be finite and positive")
    selected = [e for e in mapping if any(e in case["factors"] for case in cases)]
    # Empty selected set is a valid baseline-only run.
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Use a new output directory; saved runs are preserved")
    output.mkdir(parents=True, exist_ok=True)
    (output / "model.jl").write_text(generate(model))
    save(output / "model.json", model)
    with (output / "cases.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", *selected])
        w.writerows(
            [[c["case"], *(c["factors"].get(e, 1.0) for e in selected)] for c in cases]
        )
    with (output / "parameters.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["enzyme", "parameter", "reference_E"])
        w.writerows(
            [
                [e, f"{mapping[e]['id']}_E", mapping[e]["kinetics"]["constants"]["E"]]
                for e in selected
            ]
        )
    (output / "products.txt").write_text("\n".join(products) + "\n")
    conserved = pools or []
    for pool in conserved:
        if not pool or set(pool) - set(model["species"]):
            raise ValueError("Unknown species in conserved pool")
        for r in model["reactions"]:
            if (
                sum(r["products"].get(s, 0) - r["reactants"].get(s, 0) for s in pool)
                != 0
            ):
                raise ValueError("Claimed pool is not conserved by the network")
    (output / "pools.txt").write_text(
        "".join(",".join(pool) + "\n" for pool in conserved)
    )
    save(
        output / "manifest.json",
        {
            "model_sha256": digest(model_path),
            "products": products,
            "cases": cases,
            "conserved_pools": conserved,
            "time": model["time"],
            "fixed": "Initial pools, unselected enzyme amounts, rate laws and all other constants",
            "units": model.get("provenance", {}).get("units", "Unconfirmed"),
            "interpretation": "Finite perturbations; not global optimality or calibrated experimental predictions",
        },
    )
    print(f"Prepared {len(cases)} cases:", output)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("model", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--products", nargs="+", default=["Apap", "Sal", "Va", "Tyr"])
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--single", nargs="+", type=float, metavar="FACTOR")
    mode.add_argument("--vary", action="append", metavar="ENZYME=FACTORS")
    mode.add_argument(
        "--variants", type=Path, help="JSON list of named cases and factor maps"
    )
    p.add_argument(
        "--pool",
        action="append",
        default=[],
        help="Comma-separated conserved species; repeat per pool",
    )
    p.add_argument(
        "--run", action="store_true", help="Also invoke the common Julia runner"
    )
    args = p.parse_args()
    try:
        vary = {}
        for spec in args.vary or []:
            enzyme, values = spec.split("=", 1)
            if enzyme in vary:
                raise ValueError("Duplicate --vary enzyme")
            vary[enzyme] = list(dict.fromkeys(float(v) for v in values.split(",")))
            if not vary[enzyme]:
                raise ValueError("Empty factor list")
        prepare(
            args.model,
            args.output,
            args.products,
            args.single or [2, 5],
            vary or None,
            load(args.variants) if args.variants else None,
            [s.split(",") for s in args.pool],
        )
        if args.run:
            subprocess.run(
                [
                    "julia",
                    f"--project={HERE}",
                    str(HERE / "simulate.jl"),
                    str(args.output.resolve()),
                ],
                check=True,
            )
    except (ValueError, KeyError, OSError) as exc:
        p.exit(1, f"Cannot prepare scan: {exc}\n")


if __name__ == "__main__":
    main()
