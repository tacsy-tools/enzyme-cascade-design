rule [
	ruleID "1.4.1.a_rev R05329"
	labelType "term"
	left [
		node [ id 4 label "H+" ]
		node [ id 10 label "NAD" ]
		edge [ source 1 target 7 label "=" ]
		edge [ source 3 target 8 label "-" ]
		edge [ source 9 target 10 label "-" ]
	]
	context [
		node [ id 0 label "_A" ]
		node [ id 1 label "C" ]
		node [ id 2 label "_B" ]
		node [ id 3 label "N" ]
		node [ id 5 label "H" ]
		node [ id 6 label "H" ]
		node [ id 7 label "O" ]
		node [ id 8 label "H" ]
		node [ id 9 label "H" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 1 target 2 label "-" ]
		edge [ source 3 target 5 label "-" ]
		edge [ source 3 target 6 label "-" ]
	]
	right [
		node [ id 4 label "H" ]
		node [ id 10 label "NAD+" ]
		edge [ source 1 target 3 label "-" ]
		edge [ source 1 target 4 label "-" ]
		edge [ source 7 target 8 label "-" ]
		edge [ source 7 target 9 label "-" ]
	]
	constrainLabelAny [
		label "_A"
		labels [ label "H" label "C" ]
	]
	constrainLabelAny [
		label "_B"
		labels [ label "H" label "C" ]
	]
]