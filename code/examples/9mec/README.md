# 9MEC aromatic cascade

The network contains 39 species and 19 reactions. Its MØD construction is in
`source/Mod/`; `network/` contains the native derivation graph, reaction SMILES,
annotated SBML and carbon-annotated JSON.

`kinetics/` separates per-reaction assignments, initial concentrations and rate
laws from the network topology. `kinetic-reference.json` supplies the reference
assignments by exact reaction stoichiometry. `model.json` and `model.jl` are
generated from these tables. The alias `Htd -> HTD` preserves the species match.

`source/9MAC03.jl` is the reference model used by `verify.py`;
`source/kineticlaws.jl` contains its factored rate definitions.
`variants.json` defines the named enzyme interventions relative to E = 0.2.
`kinetic-reference.json` records the example parameter set. Physical concentration
and time units require application-specific interpretation.

Apap denotes paracetamol, Sal salicylate, Va vanillate and Tyr tyrosine. The
SAM pool is finite and has no regeneration reaction in this example.

See the [repository README](../../../README.md) for the complete design example.
