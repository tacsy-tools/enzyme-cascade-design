"""Print saved query tables, full pathways or kinetic endpoint tables; no solver."""

import argparse
import csv
import tomllib
from pathlib import Path

from common import load


def main():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="command", required=True)
    for command in ["table", "matrix", "pathway", "endpoints"]:
        sub = subs.add_parser(command)
        sub.add_argument("input", type=Path)
    args = p.parse_args()
    if args.command == "matrix":
        data = {}
        for path in args.input.glob("*.json"):
            d = load(path)
            if set(d.get("query_sources", {})) == {"PYR"} and set(
                d.get("query_targets", {})
            ) == {"3HP"}:
                data[d["query_sources"]["PYR"], d["query_targets"]["3HP"]] = d[
                    "metrics"
                ]
        if not data:
            p.error("No saved PYR -> 3HP queries in this directory")
        cols = sorted({j for i, j in data})
        print("Cells: total efficiency % / distinct reactions / auxiliary C")
        print(f"{'PYR / 3HP':<12}" + "".join(f"{j:>21}" for j in cols))
        for i in sorted({i for i, j in data}):
            cells = []
            for j in cols:
                m = data.get((i, j))
                cells.append(
                    "missing"
                    if m is None
                    else f"{m['total_efficiency']:.1f} / {m['reaction_count']} / {m['auxiliary_carbon_in']:g}"
                )
            print(f"{i:<12}" + "".join(f"{cell:>21}" for cell in cells))
    elif args.command == "endpoints":
        with (args.input / "endpoints.csv").open() as f:
            rows = list(csv.DictReader(f))
        manifest = args.input / "manifest.json"
        metadata = (
            load(manifest)
            if manifest.exists()
            else tomllib.loads((args.input / "manifest.toml").read_text())
        )
        products = metadata["products"]
        width = max(13, max(map(len, products)) + 2)
        print(f"{'case':<34}" + "".join(f"{s:>{width}}" for s in products))
        for row in rows:
            print(
                f"{row['case']:<34}"
                + "".join(f"{float(row[s]):{width}.6g}" for s in products)
            )
    elif args.command == "table":
        files = (
            sorted(args.input.glob("*.json")) if args.input.is_dir() else [args.input]
        )
        print(
            f"{'query':<28} {'aux C':>8} {'eta-S %':>9} {'total %':>9} {'reactions':>10} {'sum flux':>9}"
        )
        for f in files:
            d = load(f)
            if "metrics" not in d:
                continue
            m = d["metrics"]
            print(
                f"{f.stem:<28} {m['auxiliary_carbon_in']:8g} {m['requested_retention_lower_bound']:9.2f} {m['total_efficiency']:9.2f} {m['reaction_count']:10d} {m['total_reaction_flux']:9d}"
            )
    else:
        d = load(args.input)
        f = d["solutions"][0]
        c = d["carbon_map"]
        label = lambda s: f"{s} ({c[s]} C)"
        for title, key in [("Inputs", "source_inflows"), ("Outputs", "sink_outflows")]:
            print(
                title + ": " + ", ".join(f"{n} {label(s)}" for s, n in f[key].items())
            )
        print("Used reactions (stoichiometric list, not firing order):")
        for r in f["reactions"]:
            sides = [
                " + ".join(
                    f"{n} {label(s)}"
                    for s, n in __import__("collections").Counter(r[side]).items()
                )
                for side in ["sources", "targets"]
            ]
            print(f"{r['reaction_id']} x{r['flow']}: {sides[0]} -> {sides[1]}")
        print("Objectives and bounds:", d["optimization"])


if __name__ == "__main__":
    main()
