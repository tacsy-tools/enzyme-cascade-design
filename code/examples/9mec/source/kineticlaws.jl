# define your custom rate law equations
MM00(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E ) / ( (km * (1 + (I1 / ki1))) + (S * (1 + (I2 / ki2))) )
MM01(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E ) / ( (km * (1 + (I1 / ki1) + (I2 / ki2))) + S ) 
MM03(E, kcat, km, S1, S2) = (kcat * E ) / ( (km * km) + (km * S1) + (km * S2) + (S1 * S2) )
MM14(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E ) / ((km * (1 + (I1 / ki1))) + (S * (1 + (I2 / ki2))))
MM17(E, kcat, km, S) = (kcat * E ) / (km + S)
MM18(E, kcat, km, S, I1, ki1) = (kcat * E ) / ((km * (1 + (I1 / ki1))) + S)
