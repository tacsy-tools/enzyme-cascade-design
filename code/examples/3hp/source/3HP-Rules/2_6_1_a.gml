rule [
	ruleID "2.6.1.a R00355"
	labelType "term"
	left [
		edge [ source 1 target 2 label "=" ]
		edge [ source 4 target 5 label "-" ]
		edge [ source 4 target 8 label "-" ]
	]
	context [
		node [ id 0 label "_A" ]
		node [ id 1 label "C" ]
		node [ id 2 label "O" ]
		node [ id 3 label "_B" ]
		node [ id 4 label "Glu" ]
		node [ id 5 label "N" ]
		node [ id 6 label "H" ]
		node [ id 7 label "H" ]
		node [ id 8 label "H" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 1 target 3 label "-" ]
		edge [ source 5 target 6 label "-" ]
		edge [ source 5 target 7 label "-" ]
	]
	right [
		edge [ source 1 target 5 label "-" ]
		edge [ source 1 target 8 label "-" ]
		edge [ source 2 target 4 label "=" ]
	]
	constrainLabelAny [
		label "_A"
		labels [ label "C" label "H" ]
	]
	constrainLabelAny [
		label "_B"
		labels [ label "C" label "H" ]
	]
]