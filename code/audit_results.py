"""Check the saved kinetic endpoints and analytical MM example."""

import argparse
import csv
import json
import math
from pathlib import Path

from common import HERE, digest, load, save


def rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))


def audit(results):
    base = results / "release/kinetics"
    unique = {}
    executed = 0
    maximum_error = 0.0
    for name, expected_count in [("single", 39), ("variants", 5), ("grid", 6)]:
        directory = base / name
        manifest = load(directory / "manifest.json")
        data = rows(directory / "endpoints.csv")
        checks = rows(directory / "checks.csv")
        assert len(data) == len(checks) == len(manifest["cases"]) == expected_count
        assert manifest["model_sha256"] == digest(HERE / "examples/9mec/model.json")
        for spec, row, check in zip(manifest["cases"], data, checks):
            assert spec["case"] == row["case"] == check["case"]
            assert check["status"] == "Success"
            error = float(check["maximum_relative_endpoint_difference"])
            assert math.isfinite(error) and error < 1e-3
            assert float(check["minimum_sampled_concentration"]) >= -1e-9
            key = tuple(
                sorted(
                    (enzyme, float(factor))
                    for enzyme, factor in spec["factors"].items()
                    if factor != 1
                )
            )
            products = {
                product: float(row[product]) for product in manifest["products"]
            }
            assert all(
                math.isfinite(value) and value >= -1e-9 for value in products.values()
            )
            if key in unique:
                assert all(
                    abs(products[p] - unique[key][p])
                    <= 1e-6 * max(abs(products[p]), 1e-12)
                    for p in products
                )
            unique[key] = products
            executed += 1
            maximum_error = max(maximum_error, error)

    residuals = []
    for row in rows(base / "tutorial/trajectory-1.csv"):
        substrate, time = float(row["S"]), float(row["time"])
        residuals.append(abs(3 * time - (2 - substrate + math.log(2 / substrate))))
        assert abs(float(row["P"]) + substrate - 2) < 1e-9
    assert residuals and max(residuals) < 1e-7

    return {
        "status": "passed",
        "nine_mec_cases": executed,
        "nine_mec_unique_conditions": len(unique),
        "maximum_relative_endpoint_tolerance_difference": maximum_error,
        "tutorial_maximum_MM_equation_residual": max(residuals),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE / "results")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    proof = audit(args.results)
    if args.output:
        save(args.output, proof)
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
