"""Independent rate probes, zero-boundary checks and source-model comparison."""

import argparse
import csv
import math
import random
import subprocess
from pathlib import Path

from common import HERE, load, require_julia
from generate_julia import generate


def flux(r, state):
    k = r["kinetics"]
    c = dict(k["constants"])
    c.update({a: state[s] for a, s in k["species"].items()})
    kind = k["type"]
    if kind in ["MM00", "MM14"]:
        d = c["km"] * (1 + c["I1"] / c["ki1"]) + c["S"] * (1 + c["I2"] / c["ki2"])
    elif kind == "MM01":
        d = c["km"] * (1 + c["I1"] / c["ki1"] + c["I2"] / c["ki2"]) + c["S"]
    elif kind == "MM03":
        d = (c["km"] + c["S1"]) * (c["km"] + c["S2"])
    elif kind == "MM17":
        d = c["km"] + c["S"]
    elif kind == "MM18":
        d = c["km"] * (1 + c["I1"] / c["ki1"]) + c["S"]
    else:
        raise ValueError(kind)
    rate = c["kcat"] * c["E"] / d
    for s, n in r["reactants"].items():
        rate *= state[s] ** n / math.factorial(n)
    return rate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        require_julia()
    except RuntimeError as exc:
        p.exit(1, f"{exc}\n")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    model = load(HERE / "examples/9mec/model.json")
    names = list(model["species"])
    rng = random.Random(42)
    states = [{s: rng.uniform(0.1, 2) for s in names} for _ in range(10)]
    states += [{**states[0], s: 0.0} for s in names]
    derivatives = []
    for state in states:
        du = dict.fromkeys(names, 0.0)
        for r in model["reactions"]:
            v = flux(r, state)
            if any(state[s] == 0 for s in r["reactants"]):
                assert v == 0
            for s, n in r["reactants"].items():
                du[s] -= n * v
            for s, n in r["products"].items():
                du[s] += n * v
        assert all(du[s] >= -1e-12 for s in names if state[s] == 0)
        derivatives.append(du)
    for filename, rows in [("states.csv", states), ("expected.csv", derivatives)]:
        with (out / filename).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=names)
            w.writeheader()
            w.writerows(rows)
    (out / "model.jl").write_text(generate(model))
    subprocess.run(
        ["julia", f"--project={HERE}", str(HERE / "verify.jl"), str(out)], check=True
    )


if __name__ == "__main__":
    main()
