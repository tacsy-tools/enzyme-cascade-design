# Usage guide

Commands run from `code/`. Put new calculations in `results/local/`; this
directory is excluded from Git. Each calculation needs a fresh output directory.

## Inspect pathways and yields

```sh
python3 show.py table results/pathways/queries/9mec
python3 show.py matrix results/pathways/queries/3hp
python3 show.py pathway results/pathways/queries/9mec/Apap.json
```

Each saved query is a separate optimization. `all-four` is an additional joint
query, with its own inputs and outputs; it is not a sum of the individual rows.
The pathway listing gives reaction multiplicities and carbon counts. It describes
a balanced reaction support, rather than a chronological firing sequence.

| Column | Meaning |
| --- | --- |
| `aux C` | Carbon atoms imported in addition to the requested source molecules |
| `eta-S %` | Conservative lower bound on requested source carbon retained in the targets |
| `total %` | Target carbon divided by all imported carbon, expressed as a percentage |
| `reactions` | Number of distinct reactions used |
| `sum flux` | Sum of integer reaction multiplicities |

Complete imported carrier molecules contribute to `aux C`. A large value can
therefore indicate supplied carbon-bearing cofactors. The structural query does
not infer cofactor-regeneration reactions or catalytic starting pools.

## Rebuild a network

Use a Python environment providing `import mod`, then install the export
dependency. The runtime is not required for the other commands.

```sh
python3 -m pip install -r requirements-export.txt
python3 network.py build 9mec --output results/local/9mec-network
python3 network.py build 3hp --rounds 7 --output results/local/3hp-network
python3 network.py check results/local/9mec-network/network.json
```

Each build exports a native derivation graph, reaction SMILES, annotated SBML and
carbon-annotated JSON. Structural exports retain reaction identities and
stoichiometry. The SBML importer accepts this release's annotations and forward
reaction representation; it does not infer kinetic laws from structures.

## Assign kinetics and generate Julia

`kinetics.py init` writes three editable files. `kinetics.csv` assigns a law and
its constants/species arguments to each reaction. `initial.csv` gives the initial
species amounts. `settings.json` defines the rate laws and simulation interval.
Stoichiometry remains in the network file.

The 9MEC laws use **mass-action prefactors**: Catalyst's `-->` contributes the
reactant factors once. A law containing the complete rate uses **`full_rate`**
and Catalyst's `=>`. Keep that distinction when adding a law; changing the arrow
without changing the expression changes the model. Enzyme amount and `kcat`
enter the supplied laws as a product.

For a small complete-rate example:

```sh
python3 generate_julia.py examples/tutorial/mm.json results/local/mm.jl
julia --project=. results/local/mm.jl results/local/mm.csv
python3 scan.py examples/tutorial/mm-activity.json --products P --single 1 \
  --pool S,P --output results/local/activity --run
```

The illustrative activity factor is 0.25. It extends the rate expression while
using the same model generator and runner.

## Supply a native Catalyst model

The generic native interface accepts a Julia model plus a TOML condition file:

```sh
julia --project=. simulate.jl --native examples/tutorial/native-mm.toml \
  results/local/native-mm
python3 show.py endpoints results/local/native-mm
```

The model implements `build_case(config, spec)` and returns a reaction system,
an ODE problem, selected products, conserved pools and optional event/derived-output
functions. The tutorial supplies this complete contract for `S -> P`. The TOML
file defines two activity settings. Additional local model files can be declared
in `includes`; they are copied alongside the saved run. Both native and generated
models use the same numerical checking kernel and result-viewing commands.

## Reproduce the example set

```sh
python3 reproduce.py --kinetics --output results/local/kinetic-batch
python3 verify.py --output results/local/rate-checks
python3 audit_results.py
```

The kinetic batch contains 39 single-enzyme cases, five named variants, six
ODO/SDH combinations, and the generic kinetic tutorials. Repeated reference
conditions are retained as checks. Every integration is checked at two
tolerances, for finite/nonnegative sampled states and for the specified conserved
pools. `verify.py` also compares independently calculated 9MEC derivatives and
the supplied reference model's trajectory.

Saved results are compact: tables retain all example cases, with sampled
trajectories for the four-branchpoint walkthrough and analytical tutorial.
Recomputation writes complete trajectories and model snapshots for every case.
