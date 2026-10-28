"""Associate a network with editable kinetics and generate Julia."""

import argparse
from pathlib import Path

from common import save
from dg_kinetics import assemble, initialize
from generate_julia import generate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="command", required=True)
    init = subs.add_parser("init")
    build = subs.add_parser("build")
    for sub in [init, build]:
        sub.add_argument("network", type=Path)
        sub.add_argument("directory", type=Path)
    init.add_argument("--import-kinetics", type=Path)
    build.add_argument(
        "output", type=Path, help="generated model.json; model.jl is written beside it"
    )
    args = p.parse_args()
    try:
        if args.command == "init":
            initialize(args.network, args.directory, args.import_kinetics)
        else:
            model = assemble(args.network, args.directory)
            save(args.output, model)
            args.output.with_suffix(".jl").write_text(generate(model))
            print("Saved", args.output, "and", args.output.with_suffix(".jl"))
    except (ValueError, KeyError, OSError) as exc:
        p.exit(1, f"Cannot prepare kinetics: {exc}\n")


if __name__ == "__main__":
    main()
