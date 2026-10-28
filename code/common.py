"""Shared JSON, provenance and strict stoichiometric validation."""

import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def counts(entries):
    result = {}
    for entry in entries:
        name, value = entry.rsplit("=", 1)
        if name in result or int(value) < 1:
            raise ValueError("Use distinct NAME=positive_integer entries")
        result[name] = int(value)
    return result


def validate_network(network):
    carbon = {s: v.get("carbon") for s, v in network["species"].items()}
    if not carbon or any(
        isinstance(c, bool) or not isinstance(c, int) or c < 0 for c in carbon.values()
    ):
        raise ValueError(
            "Every species needs an explicit nonnegative integer carbon count"
        )
    identifiers = set()
    for r in network["reactions"]:
        if r["id"] in identifiers:
            raise ValueError(f"Duplicate reaction ID: {r['id']}")
        identifiers.add(r["id"])
        totals = []
        for side in ("reactants", "products"):
            for s, n in r[side].items():
                if (
                    s not in carbon
                    or isinstance(n, bool)
                    or not isinstance(n, int)
                    or n < 1
                ):
                    raise ValueError(f"Invalid stoichiometry: {r['id']}, {s}={n}")
            totals.append(sum(carbon[s] * n for s, n in r[side].items()))
        if totals[0] != totals[1]:
            raise ValueError(f"Carbon imbalance: {r['id']}: {totals}")
        if "bounds" in r:
            lo, hi = r["bounds"]
            if (
                any(
                    isinstance(v, bool)
                    or not isinstance(v, (int, float))
                    or not math.isfinite(v)
                    for v in (lo, hi)
                )
                or not 0 <= lo <= hi
            ):
                raise ValueError(f"Expected finite forward bounds for {r['id']}")
    if not identifiers:
        raise ValueError("Network has no reactions")
    return carbon
