rule [
	ruleID "4.3.1.a_rev R04071"
	labelType "term"
	left [
		edge [ source 2 target 3 label "=" ]
		edge [ source 4 target 9 label "-" ]
	]
	context [
		node [ id 0 label "O" ]
		node [ id 1 label "C" ]
		node [ id 2 label "C" ]
		node [ id 3 label "C" ]
		node [ id 4 label "N" ]
		node [ id 5 label "_A" ]
		node [ id 6 label "_B" ]
		node [ id 7 label "_C" ]
		node [ id 8 label "_D" ]
		node [ id 9 label "H" ]
		node [ id 10 label "_E" ]
		node [ id 11 label "_F" ]
		edge [ source 0 target 1 label "=" ]
		edge [ source 1 target 2 label "-" ]
		edge [ source 1 target 11 label "-" ]
		edge [ source 2 target 10 label "-" ]
		edge [ source 3 target 7 label "-" ]
		edge [ source 3 target 8 label "-" ]
		edge [ source 4 target 5 label "-" ]
		edge [ source 4 target 6 label "-" ]
	]
	right [
		edge [ source 2 target 3 label "-" ]
		edge [ source 2 target 9 label "-" ]
		edge [ source 3 target 4 label "-" ]
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
        constrainLabelAny [
                label "_D"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
        ]
        constrainLabelAny [
                label "_E"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
        ]
        constrainLabelAny [
                label "_F"
                labels [ label "C" label "H" label "N" label "O" label "S" ]
        ]
]
