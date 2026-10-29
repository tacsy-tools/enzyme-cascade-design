"""Generate a Julia/Catalyst ODE script from a small reaction/kinetics JSON file."""

import argparse
import ast
import json
import math
import re
from pathlib import Path


def validate(model):
    def identifier(name):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name):
            raise ValueError(f"Invalid Julia identifier: {name}")

    def number(value):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(f"Expected finite, nonnegative number: {value}")

    species = model["species"]
    for name, info in species.items():
        identifier(name)
        number(info["initial"])
    span = model["time"]["span"]
    if (
        len(span) != 2
        or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in span)
        or span[1] <= span[0]
    ):
        raise ValueError("Expected increasing finite time span")
    points = model["time"]["save_points"]
    if not isinstance(points, int) or points < 2:
        raise ValueError("save_points must be an integer >= 2")
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    )
    for kind, law in model["rate_laws"].items():
        identifier(kind)
        for arg in law["arguments"]:
            identifier(arg)
        tree = ast.parse(law["expression"].replace("^", "**"), mode="eval")
        if any(not isinstance(n, allowed) for n in ast.walk(tree)):
            raise ValueError(f"Unsupported expression for {kind}")
        if {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} - set(
            law["arguments"]
        ):
            raise ValueError(f"Unknown argument in {kind}")
    ids = set()
    for reaction in model["reactions"]:
        identifier(reaction["id"])
        if reaction["id"] in ids:
            raise ValueError(f"Duplicate reaction ID: {reaction['id']}")
        ids.add(reaction["id"])
        for side in ("reactants", "products"):
            for name, count in reaction[side].items():
                if (
                    name not in species
                    or isinstance(count, bool)
                    or not isinstance(count, int)
                    or count < 1
                ):
                    raise ValueError(f"Invalid stoichiometry: {name}={count}")
        kin = reaction["kinetics"]
        law = model["rate_laws"][kin["type"]]
        if set(kin["species"]) & set(kin["constants"]) or set(kin["species"]) | set(
            kin["constants"]
        ) != set(law["arguments"]):
            raise ValueError(
                f"Kinetic arguments missing/duplicated in {reaction['id']}"
            )
        if set(kin["species"].values()) - set(species):
            raise ValueError(f"Unknown kinetic species in {reaction['id']}")
        for value in kin["constants"].values():
            number(value)
        if kin["mode"] not in ("mass_action", "full_rate"):
            raise ValueError(f"Unknown rate mode: {kin['mode']}")


def generate(model, full_rates=False):
    validate(model)
    lines = [
        "# Generated from the JSON input; edit the input, then regenerate.",
        *Path(__file__).with_name("julia_runtime.jl").read_text().splitlines(),
        "",
        "using Catalyst",
        "using DifferentialEquations",
        "using DelimitedFiles",
        "",
    ]
    for kind, law in model["rate_laws"].items():
        lines.append(f"{kind}({', '.join(law['arguments'])}) = {law['expression']}")
    lines += ["", "rn = @reaction_network begin"]
    parameters = {}
    for r in model["reactions"]:
        k = r["kinetics"]
        arguments = []
        for arg in model["rate_laws"][k["type"]]["arguments"]:
            if arg in k["species"]:
                arguments.append(k["species"][arg])
            else:
                name = f"{r['id']}_{arg}"
                arguments.append(name)
                parameters[name] = k["constants"][arg]
        sides = [
            " + ".join(
                f"{count}*{name}" if count != 1 else name
                for name, count in r[s].items()
            )
            or "0"
            for s in ("reactants", "products")
        ]
        arrow = "=>" if full_rates or k["mode"] == "full_rate" else "-->"
        lines += [
            f"    # {r['id']}: {k['type']}",
            f"    {k['type']}({', '.join(arguments)}), {sides[0]} {arrow} {sides[1]}",
        ]
    lines += ["end", "", "u0 = ["]
    lines += [
        f"    :{name} => {info['initial']}," for name, info in model["species"].items()
    ]
    lines += ["]", "", "p = ["] + [
        f"    :{name} => {value}," for name, value in parameters.items()
    ]
    lines += [
        "]",
        f"tspan = ({model['time']['span'][0]}, {model['time']['span'][1]})",
        "problem = ODEProblem(rn, u0, tspan, p)",
        "",
        "# Including this file exposes rn, u0, p, and problem for further analysis.",
        "if abspath(PROGRAM_FILE) == @__FILE__",
        f"    times = range(tspan[1], tspan[2]; length={model['time']['save_points']})",
        "    solution = solve(problem, Rosenbrock23(); saveat=times, reltol=1e-8, abstol=1e-10)",
        '    SciMLBase.successful_retcode(solution) || error("ODE solve failed: $(solution.retcode)")',
        '    output = isempty(ARGS) ? splitext(@__FILE__)[1] * ".csv" : ARGS[1]',
        '    header = ["time"; string.(species(rn))]',
        "    data = hcat(solution.t, permutedims(Array(solution)))",
        "    writedlm(output, vcat(permutedims(header), data), ',')",
        '    println("Saved ", output, "; solver status: ", solution.retcode)',
        "end",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--full-rates",
        action="store_true",
        help="Explicitly replace legacy --> by full-rate => kinetics",
    )
    args = parser.parse_args()
    try:
        source = generate(json.loads(args.input.read_text()), args.full_rates)
    except (ValueError, KeyError, SyntaxError) as error:
        parser.exit(1, f"Invalid input: {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(source)
    print("Generated", args.output)
