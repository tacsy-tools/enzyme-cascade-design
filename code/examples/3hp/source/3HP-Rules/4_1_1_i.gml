rule [
	ruleID "4.1.1.i R05722"
	labelType "term"
	left [
		node [ id 8 label "NAD+" ]
		node [ id 10 label "H" ]
		edge [ source 1 target 3 label "-" ]
		edge [ source 3 target 5 label "-" ]
		edge [ source 5 target 6 label "-" ]
		edge [ source 9 target 10 label "-" ]
	]
	context [
		node [ id 0 label "_A" ]
		node [ id 1 label "C" ]
		node [ id 2 label "O" ]
		node [ id 3 label "C" ]
		node [ id 4 label "O" ]
		node [ id 5 label "O" ]
		node [ id 6 label "H" ]
		node [ id 7 label "CoA" ]
		node [ id 9 label "S" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 1 target 2 label "=" ]
		edge [ source 3 target 4 label "=" ]
		edge [ source 7 target 9 label "-" ]
	]
	right [
		node [ id 8 label "NAD" ]
		node [ id 10 label "H+" ]
		edge [ source 1 target 9 label "-" ]
		edge [ source 3 target 5 label "=" ]
		edge [ source 6 target 8 label "-" ]
	]
	constrainLabelAny [
		label "_A"
		labels [ label "O" label "S" label "C" ]
	]
]