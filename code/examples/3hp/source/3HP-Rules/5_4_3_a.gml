rule [
	ruleID "5.4.3.a R01091"
	labelType "term"
	left [
		edge [ source 2 target 7 label "-" ]
		edge [ source 3 target 4 label "-" ]
	]
	context [
		node [ id 0 label "O" ]
		node [ id 1 label "C" ]
		node [ id 2 label "C" ]
		node [ id 3 label "C" ]
		node [ id 4 label "H" ]
		node [ id 5 label "_A" ]
		node [ id 6 label "_B" ]
		node [ id 7 label "N" ]
		node [ id 8 label "_C" ]
		node [ id 9 label "O" ]
		node [ id 10 label "H" ]
		node [ id 11 label "H" ]
		node [ id 12 label "H" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 0 target 10 label "-" ]
		edge [ source 1 target 2 label "-" ]
		edge [ source 1 target 9 label "=" ]
		edge [ source 2 target 3 label "-" ]
		edge [ source 2 target 8 label "-" ]
		edge [ source 3 target 5 label "-" ]
		edge [ source 3 target 6 label "-" ]
		edge [ source 7 target 11 label "-" ]
		edge [ source 7 target 12 label "-" ]
	]
	right [
		edge [ source 2 target 4 label "-" ]
		edge [ source 3 target 7 label "-" ]
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
