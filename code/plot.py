"""Plot product trajectories from a saved generated or native model run."""

import argparse
import csv
import math
import tomllib
from pathlib import Path

from common import load


def plot_run(directory, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path = directory / "manifest.json"
    manifest = (
        load(path)
        if path.exists()
        else tomllib.loads((directory / "manifest.toml").read_text())
    )
    products = manifest["products"]
    columns = min(2, len(products))
    rows = math.ceil(len(products) / columns)
    figure, axes = plt.subplots(rows, columns, figsize=(9, 3 * rows), squeeze=False)
    for index, case in enumerate(manifest["cases"], start=1):
        with (directory / f"trajectory-{index}.csv").open() as handle:
            values = list(csv.DictReader(handle))
        times = [float(row["time"]) for row in values]
        label = case.get("case", case.get("name"))
        if len(label) > 36:
            label = "Changed enzyme mixture"
        for axis, product in zip(axes.flat, products):
            axis.plot(times, [float(row[product]) for row in values], label=label)
    for axis, product in zip(axes.flat, products):
        axis.set(
            title=product, xlabel="Time (model scale)", ylabel="Amount (model scale)"
        )
        axis.grid(alpha=0.2)
        axis.legend(frameon=False, fontsize=8)
    for axis in list(axes.flat)[len(products) :]:
        axis.set_visible(False)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, help="Saved run directory, including trajectories"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plot_run(args.input, args.output)
    print("Saved", args.output)


if __name__ == "__main__":
    main()
