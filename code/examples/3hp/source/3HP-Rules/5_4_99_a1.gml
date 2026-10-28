rule [
	ruleID "5.4.99.a1 R01181"
	labelType "term"
	left [
		edge [ source 2 target 10 label "-" ]
		edge [ source 4 target 7 label "-" ]
	]
	context [
		node [ id 0 label "_A" ]
		node [ id 1 label "C" ]
		node [ id 2 label "C" ]
		node [ id 3 label "_B" ]
		node [ id 4 label "C" ]
		node [ id 5 label "H" ]
		node [ id 6 label "O" ]
		node [ id 7 label "H" ]
		node [ id 8 label "H" ]
		node [ id 9 label "H" ]
		node [ id 10 label "_C" ]
		edge [ source 0 target 1 label "-" ]
		edge [ source 1 target 2 label "-" ]
		edge [ source 1 target 6 label "=" ]
		edge [ source 2 target 4 label "-" ]
		edge [ source 2 target 5 label "-" ]
		edge [ source 0 target 3 label "-" ]
		edge [ source 4 target 8 label "-" ]
		edge [ source 4 target 9 label "-" ]
	]
	right [
		edge [ source 2 target 7 label "-" ]
		edge [ source 4 target 10 label "-" ]
	]
	constrainLabelAny [
		label "alt(_A,_B)"
		labels [ label "alt(O,H)" label "alt(S,CoA)" ]
	]
        constrainLabelAny [
                label "_C"
                labels [ label "C" label "H" ]
	]
]
