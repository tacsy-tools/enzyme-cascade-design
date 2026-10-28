import mod

include("common.py")

strat = (
     addSubset(inputGraphs)
     >> rightPredicate[
     lambda d: all(g in known_mols for g in d.right)
     ](repeat(inputRules))
)

# construct derivation graph
dg = DG(graphDatabase=known_mols, labelSettings=ls)
dg.build().execute(strat)
dg.print()

print('\n####=== reas in compound name ===###')
# print list of reactions as reaction smiles
for e in dg.edges:
    printRea(e)

print('\n####=== translate compounds SMIs to names ===###')
for v in dg.vertices:
    print(f'{v.graph.smiles} <=> {v.graph.name}')

print('\n####=== reas in compound name ===###\n')
# print list of reactions as compound names
for e in dg.edges:
    printReaWithNames(e)

post.flushCommands()
