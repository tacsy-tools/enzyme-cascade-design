## Define grammar defining the chemical space

# co-substrates
glu = Graph.fromDFS('[Glu](N)[H]', 'Glu')
m2og  = Graph.fromDFS('[Glu]=O', '2OG')
nadplus = Graph.fromDFS('[NAD+]', 'NAD+')
nadh = Graph.fromDFS('[NAD][H]', 'NADH')
coa = Graph.fromDFS('[CoA]S', 'CoA')
co2 = Graph.fromSMILES('O=C=O', 'CO2')
h2o = Graph.fromSMILES('O', 'H2O')
nh3 = Graph.fromSMILES('N', 'NH3')
atp = Graph.fromDFS('[ADP]OP(=O)(O)O', 'ATP')
adp = Graph.fromDFS('[ADP]O', 'ADP')
pi  = Graph.fromSMILES('O=P(O)(O)O', 'Pi')
h   = Graph.fromSMILES('[H+]', 'H+')

cosubsts = [glu, m2og, nadplus, nadh, coa, co2, h2o, nh3, atp, adp, pi, h]

# substrates
pyr = Graph.fromSMILES('CC(=O)C(=O)O', 'PYR')
m3hp = Graph.fromSMILES('OCCC(=O)O', '3HP')
ala = Graph.fromSMILES('CC(N)C(=O)O', 'ALA')
prop = Graph.fromSMILES('C=CC(=O)O', 'PROP')
acrcoa = Graph.fromDFS('C=CC(=O)S[CoA]', 'ACRCoA')

for m in inputGraphs if globals().get('render', True) else []:
    p = GraphPrinter()
    p.setMolDefault()
    p.withIndex = True
    m.print(p)

for file in sorted(list(filter(lambda x: x.endswith('.gml'),
                               os.listdir('./3HP-Rules/')))):
    #if file in ['5_4_99_a.gml', '5_4_99_a_rev.gml']: continue 
    print('Reading rule Rules/' + file) 
    Rule.fromGMLFile('./3HP-Rules/' + file)

if globals().get('render', True):
    post.summarySection("DPO Diagramms of Rule(s)")
for r in inputRules if globals().get('render', True) else []:
    p = GraphPrinter()
    p.setReactionDefault()
    p.withIndex = True
    r.print(p)
