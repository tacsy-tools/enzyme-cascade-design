rule [
	ruleID "4.1.1.c R06830"
	labelType "term"
	left [
		edge [ source 1 target 2 label "-" ]
		edge [ source 1 target 6 label "-" ]
		edge [ source 6 target 9 label "-" ]
	]
	context [
		node [ id 0 label "O" ]
		node [ id 1 label "C" ]
		node [ id 2 label "C" ]
		node [ id 3 label "N" ]
		node [ id 4 label "_A" ]
		node [ id 5 label "_B" ]
		node [ id 6 label "O" ]
		node [ id 7 label "H" ]
		node [ id 8 label "H" ]
		node [ id 9 label "H" ]
		edge [ source 0 target 1 label "=" ]
		edge [ source 2 target 3 label "-" ]
		edge [ source 2 target 4 label "-" ]
		edge [ source 2 target 5 label "-" ]
		edge [ source 3 target 7 label "-" ]
		edge [ source 3 target 8 label "-" ]
	]
	right [
		edge [ source 1 target 6 label "=" ]
		edge [ source 2 target 9 label "-" ]
	]
	constrainLabelAny [
		label "_A"
		labels [ label "N" label "C" label "H" ]
	]
	constrainLabelAny [
		label "_B"
		labels [ label "N" label "C" label "H" ]
	]
]