rule [
	ruleID "4.2.1.b R02490"
	labelType "term"
	left [
		edge [ source 1 target 2 label "-" ]
		edge [ source 1 target 4 label "-" ]
		edge [ source 4 target 7 label "-" ]
	]
	context [
		node [ id 0 label "C" ]
		node [ id 1 label "C" ]
		node [ id 2 label "O" ]
		node [ id 3 label "_A" ]
		node [ id 4 label "C" ]
		node [ id 5 label "_B" ]
		node [ id 6 label "_C" ]
		node [ id 7 label "H" ]
		node [ id 8 label "S" ]
		node [ id 9 label "O" ]
		node [ id 10 label "H" ]
		node [ id 11 label "CoA" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 0 target 8 label "-" ]
		edge [ source 0 target 9 label "=" ]
		edge [ source 1 target 3 label "-" ]
		edge [ source 2 target 10 label "-" ]
		edge [ source 4 target 5 label "-" ]
		edge [ source 4 target 6 label "-" ]
		edge [ source 8 target 11 label "-" ]
	]
	right [
		edge [ source 1 target 4 label "=" ]
		edge [ source 2 target 7 label "-" ]
	]
        constrainLabelAny [
                label "_A"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
        ]
        constrainLabelAny [
                label "_B"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
        ]
        constrainLabelAny [
                label "_C"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
        ]

]
