# 3HP structural example

The seven-round MØD expansion in `source/` gives 83 species and 248 reactions.
Products are limited to at most five explicit carbon atoms, excluding atoms
hidden inside abbreviated carrier labels. The native DG, standard reaction
SMILES with labelled dummy atoms, annotated SBML and carbon-annotated network
are supplied together. The query matrix uses exact PYR consumption and exact
3HP production; arbitrary auxiliary imports except target import remain allowed.

`cofactor-carbon.json` contains fixed full carbon counts for the abbreviated
groups ADP (10), CoA (21), Glu (5), NAD (21), NAD+ (21). These are inherited from
the project's original 3HP analysis. Explicit attached atoms are counted
separately. No abbreviated group silently becomes zero carbon.

Balanced net carrier recycling may require catalytic seed pools; the query does
not infer a firing sequence or initial concentrations. Individual atom provenance
and thermodynamic/kinetic feasibility are outside this structural calculation.
