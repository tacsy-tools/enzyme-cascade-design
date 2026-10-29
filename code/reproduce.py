"""Recompute the bundled kinetic design examples."""

import argparse
import subprocess
from pathlib import Path

from common import HERE, load, require_julia


def kinetics(output):
    from scan import prepare

    model = HERE / "examples/9mec/model.json"
    products = ["Apap", "Sal", "Va", "Tyr"]
    pools = [["Atp", "Adp", "Amp"], ["Nadh", "Nad_plus"], ["Sam", "Sah"]]
    prepare(model, output / "single", products, factors=[2, 5], pools=pools)
    prepare(
        model,
        output / "variants",
        products,
        variants=load(HERE / "examples/9mec/variants.json"),
        pools=pools,
    )
    prepare(
        model,
        output / "grid",
        products,
        vary={"ODO": [1, 0.5, 0.2], "SDH": [1, 5]},
        pools=pools,
    )
    prepare(
        HERE / "examples/tutorial/mm.json",
        output / "tutorial",
        ["P"],
        variants=[],
        pools=[["S", "P"]],
    )
    prepare(
        HERE / "examples/tutorial/mm-activity.json",
        output / "activity",
        ["P"],
        variants=[],
        pools=[["S", "P"]],
    )
    subprocess.run(
        [
            "julia",
            f"--project={HERE}",
            str(HERE / "simulate.jl"),
            *(
                str((output / case).resolve())
                for case in ["single", "variants", "grid", "tutorial", "activity"]
            ),
        ],
        check=True,
    )
    subprocess.run(
        [
            "julia",
            f"--project={HERE}",
            str(HERE / "simulate.jl"),
            "--native",
            str(HERE / "examples/tutorial/native-mm.toml"),
            str((output / "native-mm").resolve()),
        ],
        check=True,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kinetics", action="store_true")
    p.add_argument("--output", type=Path, default=HERE / "results/reproduced")
    args = p.parse_args()
    if not args.kinetics:
        p.error("Select --kinetics")
    try:
        require_julia()
    except RuntimeError as exc:
        p.exit(1, f"{exc}\n")
    if args.output.exists() and any(args.output.iterdir()):
        p.error("Use a new empty output directory")
    if args.kinetics:
        kinetics(args.output / "kinetics")


if __name__ == "__main__":
    main()
