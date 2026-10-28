rule [
	ruleID "3.1.2.a R03157"
	labelType "term"
	left [
		edge [ source 0 target 1 label "-" ]
		edge [ source 5 target 7 label "-" ]
	]
	context [
		node [ id 0 label "C" ]
		node [ id 1 label "S" ]
		node [ id 2 label "CoA" ]
		node [ id 3 label "_A" ]
		node [ id 4 label "O" ]
		node [ id 5 label "O" ]
		node [ id 6 label "H" ]
		node [ id 7 label "H" ]
		edge [ source 0 target 3 label "-" ]
		edge [ source 0 target 4 label "=" ]
		edge [ source 1 target 2 label "-" ]
		edge [ source 5 target 6 label "-" ]
	]
	right [
		edge [ source 0 target 5 label "-" ]
		edge [ source 1 target 7 label "-" ]
	]
        constrainLabelAny [
                label "_A"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
	]
]
