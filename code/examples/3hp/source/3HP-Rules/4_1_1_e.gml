rule [
	ruleID "4.1.1.e R04380"
	labelType "term"
	left [
		edge [ source 1 target 2 label "-" ]
		edge [ source 1 target 10 label "-" ]
		edge [ source 2 target 5 label "-" ]
		edge [ source 5 target 6 label "-" ]
		edge [ source 10 target 11 label "-" ]
	]
	context [
		node [ id 0 label "O" ]
		node [ id 1 label "C" ]
		node [ id 2 label "C" ]
		node [ id 3 label "_A" ]
		node [ id 4 label "_B" ]
		node [ id 5 label "C" ]
		node [ id 6 label "O" ]
		node [ id 7 label "_C" ]
		node [ id 8 label "_D" ]
		node [ id 9 label "_E" ]
		node [ id 10 label "O" ]
		node [ id 11 label "H" ]
		edge [ source 0 target 1 label "=" ]
		edge [ source 2 target 3 label "-" ]
		edge [ source 2 target 4 label "-" ]
		edge [ source 5 target 8 label "-" ]
		edge [ source 5 target 9 label "-" ]
		edge [ source 6 target 7 label "-" ]
	]
	right [
		edge [ source 1 target 10 label "=" ]
		edge [ source 2 target 5 label "=" ]
		edge [ source 6 target 11 label "-" ]
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
		labels [ label "C" label "H" ]
	]
	constrainLabelAny [
	        label "_D"
		labels [ label "C" label "H" label "N" label "O" label "S" ]
	]
	constrainLabelAny [
	        label "_E"
		labels [ label "C" label "H" label "N" label "O" label "S" ]
	]
]
