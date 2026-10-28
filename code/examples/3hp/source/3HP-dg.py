## Construct derivation graph

ls = LabelSettings(LabelType.Term, LabelRelation.Specialisation)
dg = DG(graphDatabase=inputGraphs, labelSettings=ls)
with dg.build() as b:
    b.execute(
        addSubset(inputGraphs)
        >> rightPredicate [
            lambda d: all(g.vLabelCount("C") <= 5 for g in d.right)
        ](repeat[globals().get('expansion_rounds', 9)](inputRules))
    )
if globals().get('render', True):
    dg.print()
