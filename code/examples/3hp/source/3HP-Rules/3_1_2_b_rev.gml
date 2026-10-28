rule [
	ruleID "3.1.2.b_rev R01172"
	labelType "term"
	left [
		node [ id 5 label "NAD+" ]
		node [ id 7 label "H" ]
		edge [ source 0 target 6 label "-" ]
		edge [ source 1 target 7 label "-" ]
	]
	context [
		node [ id 0 label "C" ]
		node [ id 1 label "S" ]
		node [ id 2 label "CoA" ]
		node [ id 3 label "_A" ]
		node [ id 4 label "O" ]
		node [ id 6 label "H" ]
		edge [ source 0 target 3 label "-" ]
		edge [ source 0 target 4 label "=" ]
		edge [ source 1 target 2 label "-" ]
	]
	right [
		node [ id 5 label "NAD" ]
		node [ id 7 label "H+" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 5 target 6 label "-" ]
	]
        constrainLabelAny [
                label "_A"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
        ]
]
