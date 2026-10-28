include("mols.py")
include("rules.py")

def printGrammar() -> None:
	post.summarySection("Molecule(s)")
	p = GraphPrinter()
	p.setMolDefault()
	#p.withIndex = True
	for m in inputGraphs:
		m.print(p)

	post.summarySection("Rule(s)")
	p = GraphPrinter()
	p.setReactionDefault()
	p.withIndex = True
	for r in inputRules:
		r.print(p)

ls = LabelSettings(LabelType.Term, LabelRelation.Specialisation)

def printRea(e: DG.HyperEdge) -> None:
	"""Print reaction from edge."""
	educts   = " + ".join(sorted(v.graph.smiles for v in e.sources))
	products = " + ".join(sorted(v.graph.smiles for v in e.targets))
	rea = f'{educts} -> {products} ; {[r.id for r in e.rules]}'
	print(rea)

def printReaWithNames(e: DG.HyperEdge) -> None:
	"""Print reaction from edge."""
	educts   = " + ".join(sorted(v.graph.name for v in e.sources))
	products = " + ".join(sorted(v.graph.name for v in e.targets))
	rea = f'{educts} -> {products} ; {[r.id for r in e.rules]}'
	print(rea)

def toFilename(basename: str) -> str:
	import time
	timestr = time.strftime("-%Y%m%d-%H%M%S")
	return basename + timestr

def dumpTrace(trace: causality.EventTrace, basename: str):
	fDG = trace.dg.dump(basename + ".dg")
	fTrace = trace.dump(basename + ".eventTrace")
	print(f'Dumped DG to file         {fDG}.')
	print(f'Dumped EventTrace to file {fTrace}.')

def loadTrace(dg, basename: str):
	trace = causality.EventTrace.load(dg, f"{basename}.eventTrace")
	return trace

def loadTraceAndDG(graphDatabase, ruleDatabase, basename: str):
	dg = DG.load(graphDatabase, ruleDatabase, f"{basename}.dg")
	return loadTrace(dg, basename)
