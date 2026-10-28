# In vitro ATP regeneration from polyphosphate and AMP by polyphosphate, Resnick (2000): https://doi.org/10.1128/aem.66.5.2045-2051.2000
# Biochemical reactions for in vitro ATP production and their applications, Jaroensuk (2023) https://doi.org/10.1016/j.mcat.2023.112937 
# EC Number: 2.7.4.3
# Homo Sapien (ph 8, 25C), Thuma, E. - https://doi.org/10.1016/0005-2744(72)90200-8
# pH range: 6.5 - 8.2 (7.9)
# Temperature range: (30)
# Km: 0.35
# Kcat: 783
# Inhibitors: ADP: 0.9 AMP: 1.6 ATP: 0.74 
rule [
    ruleID "AdK-catalysed ATP Regeneration"
    labelType "term"
    left [
        edge [ source 8 target 12 label "-" ]
        edge [ source 16 target 20 label "-" ]
    ]
    context [ 
        node [ id 1 label "Ad" ]
        node [ id 2 label "O" ]
        node [ id 3 label "P" ]
        node [ id 4 label "O" ]
        node [ id 5 label "O" ]
        node [ id 6 label "H" ]
        node [ id 7 label "O" ]
        node [ id 8 label "P" ]
        node [ id 9 label "O" ]
        node [ id 10 label "O" ]
        node [ id 11 label "H" ]
        node [ id 12 label "O" ]
        node [ id 13 label "H" ]
        node [ id 14 label "Ad" ]
        node [ id 15 label "O" ]
        node [ id 16 label "P" ]
        node [ id 17 label "O" ]
        node [ id 18 label "O" ]
        node [ id 19 label "H" ]
        node [ id 20 label "O" ]
        node [ id 21 label "P" ]
        node [ id 22 label "O" ]
        node [ id 23 label "O" ]
        node [ id 24 label "H" ]
        node [ id 25 label "O" ]
        node [ id 26 label "H" ]
        edge [ source 1 target 2 label "-" ]
        edge [ source 2 target 3 label "-" ]
        edge [ source 3 target 4 label "=" ]
        edge [ source 3 target 5 label "-" ]
        edge [ source 3 target 7 label "-" ]
        edge [ source 5 target 6 label "-" ]
        edge [ source 7 target 8 label "-" ]
        edge [ source 8 target 9 label "=" ]
        edge [ source 8 target 10 label "-" ]
        edge [ source 10 target 11 label "-" ]
        edge [ source 12 target 13 label "-" ]
        edge [ source 14 target 15 label "-" ]
        edge [ source 15 target 16 label "-" ]
        edge [ source 16 target 17 label "=" ]
        edge [ source 16 target 18 label "-" ]
        edge [ source 18 target 19 label "-" ]
        edge [ source 20 target 21 label "-" ]
        edge [ source 21 target 22 label "=" ]
        edge [ source 21 target 23 label "-" ]
        edge [ source 21 target 25 label "-" ]
        edge [ source 23 target 24 label "-" ]
        edge [ source 25 target 26 label "-" ]
    ]
    right [
        edge [ source 8 target 20 label "-" ]
        edge [ source 16 target 12 label "-" ]
    ]
]