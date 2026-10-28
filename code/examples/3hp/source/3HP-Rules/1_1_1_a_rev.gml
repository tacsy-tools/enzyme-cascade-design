rule [
	ruleID "1.1.1.a_rev R02528"
	labelType "term"
	left [
		node [ id 0 label "H+" ]
		node [ id 6 label "NAD" ]
		edge [ source 1 target 2 label "=" ]
		edge [ source 3 target 6 label "-" ]
	]
	context [
		node [ id 1 label "O" ]
		node [ id 2 label "C" ]
		node [ id 3 label "H" ]
		node [ id 4 label "_Z1" ]
		node [ id 5 label "_Z2" ]
		edge [ source 2 target 4 label "-" ]
		edge [ source 2 target 5 label "-" ]
	]
	right [
		node [ id 0 label "H" ]
		node [ id 6 label "NAD+" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 1 target 2 label "-" ]
		edge [ source 2 target 3 label "-" ]
	]
	constrainLabelAny [
		label "_Z1"
		labels [ label "C" label "H" ]
	]
	constrainLabelAny [
		label "_Z2"
		labels [ label "C" label "H" ]
	]
]