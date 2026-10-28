using Catalyst
using OrdinaryDiffEq  # Required for solving the ODE
using Plots           # Required for plotting the time course

# Rate prefactors: --> supplies the reactant concentration factors once,
# including consumed cofactors. Do not multiply S or S1*S2 here again.
MM00(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E) / ( (km * (1 + (I1 / ki1))) + (S * (1 + (I2 / ki2))) )
MM01(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E) / ( (km * (1 + (I1 / ki1) + (I2 / ki2))) + S )
MM03(E, kcat, km, S1, S2) = (kcat * E) / ( (km * km) + (km * S1) + (km * S2) + (S1 * S2) )
MM14(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E) / ((km * (1 + (I1 / ki1))) + (S * (1 + (I2 / ki2))))
MM17(E, kcat, km, S) = (kcat * E) / (km + S)
MM18(E, kcat, km, S, I1, ki1) = (kcat * E) / ((km * (1 + (I1 / ki1))) + S)

# Define your reaction network
rn = @reaction_network begin
    MM00(DHQ, kcat_1, Km_1, Dhq, I, Ki, I, Ki), Dhq --> Dhs + H2O
    MM01(SDH,kcat_1r, Km_1r, Dhs, Dhq, Kr2, Skm, Kr3), Dhs + H_plus + Nadh --> Nad_plus + Skm
    MM18(SK, kcat_2, Km_2, Skm, Atp, K22), Atp + Skm --> Adp + S3p
    MM03(EPS, kcat_3, Km_3, S3p, Pep), Pep + S3p --> Epsp + Pi
    MM18(CS, kcat_4, Km_4, Epsp, Nadh, K42), Epsp --> Cha + Pi
    MM03(PABB, kcat_4r, Km_4r, Cha, Gln), Cha + Gln --> Adc + Glu
    MM14(ADC, kcat_5, Km_5, Adc, I, Ki, I, Kii), Adc --> AmBez + Pyr
    MM14(ABC, kcat_6, Km_6, AmBez, I, Ki, I, Kii), AmBez + H_plus + Nadh + O2 --> AmPhOH + CO2 + H2O + Nad_plus
    MM14(ADH, kcat_7, Km_7, AmPhOH, I, Ki, I, Kii), AcCoA + AmPhOH --> Apap + CoA
    MM17(GBH, kcat_8, Km_8, Cha), Cha --> Iso
    MM17(DHL, kcat_9, Km_9, Iso), Iso --> Pyr + Sal
    MM17(LCH, kcat_10, Km_10, Cha), Cha --> Ppa
    MM17(BNH, kcat_11, Km_11, Ppa), Nad_plus + Ppa --> CO2 + H_plus + Hpp + Nadh
    MM03(KMN, kcat_12, Km_12, Hpp, Htd), Htd + Hpp --> Imz + Tyr
    MM14(ODO, kcat_13, Km_13, Dhs, I, Ki, I, Kii), Dhs --> H2O + Pca
    MM17(OMT, kcat_14, Km_14, Pca), Pca + Sam --> Sah + Va
    MM17(THU, kcat_15, Km_15, Adp), Adp + Adp --> Amp + Atp
    MM17(GAO, kcat_16, Km_16, Deoxy), Deoxy --> Dhq + Pi
    MM18(DHA, kcat_17, Km_17, E4p, Pep, Kr5), E4p + H2O + Pep --> Deoxy + Pi
end

# 1. Map your species to their initial concentrations
u0 = [
    :Dhq => 1.0, :Dhs => 0.0, :H2O => 10.0, :H_plus => 1.0, :Nadh => 2.0, 
    :Nad_plus => 0.0, :Skm => 0.0, :Atp => 2.0, :Adp => 0.0, :S3p => 0.0, 
    :Pep => 1.5, :Epsp => 0.0, :Pi => 0.0, :Cha => 0.0, :Gln => 1.0, 
    :Adc => 0.0, :Glu => 0.0, :Pyr => 0.0, :AmBez => 0.0, :O2 => 1.0, 
    :AmPhOH => 0.0, :CO2 => 0.0, :AcCoA => 1.0, :Apap => 0.0, :CoA => 0.0, 
    :Iso => 0.0, :Sal => 0.0, :Ppa => 0.0, :Hpp => 0.0, :Htd => 1.0, 
    :Imz => 0.0, :Tyr => 0.0, :Pca => 0.0, :Sam => 1.0, :Sah => 0.0, 
    :Va => 0.0, :Amp => 0.0, :Deoxy => 0.0, :E4p => 1.0
]

# 2. Define the simulation time span
tspan = (0.0, 1000.0)

# 3. FIX: Map your kinetic and enzyme values explicitly to the Catalyst parameters
p = [
    :kcat_1 => 3.2, :kcat_1r => 0.405, :kcat_2 => 30.8, :kcat_3 => 8.6, :kcat_4 => 0.8,
    :kcat_4r => 0.00544, :kcat_5 => 1.5, :kcat_6 => 0.98, :kcat_7 => 18.68, :kcat_8 => 0.67,
    :kcat_9 => 0.035, :kcat_10 => 1.995, :kcat_11 => 0.655, :kcat_12 => 428.4, :kcat_13 => 153.7,
    :kcat_14 => 0.032, :kcat_15 => 783, :kcat_16 => 16, :kcat_17 => 21.83,
    
    :DHQ => 0.2, :SDH => 0.2, :SK => 0.2, :EPS => 0.2, :CS => 0.2, :PABB => 0.2,
    :ADC => 0.2, :ABC => 0.2, :ADH => 0.2, :GBH => 0.2, :DHL => 0.2, :LCH => 0.2,
    :BNH => 0.2, :KMN => 0.2, :ODO => 0.2, :OMT => 0.2, :THU => 0.2, :GAO => 0.2, :DHA => 0.2,
    
    :Km_1 => 0.02, :Km_1r => 0.287, :Km_2 => 0.2, :Km_3 => 0.1, :Km_4 => 0.0027,
    :Km_4r => 0.0016, :Km_5 => 0.015, :Km_6 => 0.02, :Km_7 => 2.22, :Km_8 => 0.007,
    :Km_9 => 0.0026, :Km_10 => 1.14, :Km_11 => 0.25, :Km_12 => 0.42, :Km_13 => 0.311,
    :Km_14 => 0.015, :Km_15 => 0.35, :Km_16 => 0.0057, :Km_17 => 0.037,
    
    :I => 0.0, :Ki => 1.0, :Kr2 => 0.42, :Kr3 => 0.14, :K22 => 0.5, :K42 => 0.043,
    :Kii => 2.0, :Kr5 => 0.015
]

# 4. Construct the ODE problem with the correct parameter array
oprob = ODEProblem(rn, u0, tspan, p)

# 5. Solve using a stable solver for complex biological systems
sol = solve(oprob, Rosenbrock23())

# 6. Plot the results
species_to_plot = [:Dhq, :Dhs, :Skm, :Epsp, :Cha, :Adc, :AmBez, :AmPhOH, :Apap, :Iso, :Sal, :Ppa, :Hpp, :Imz, :Tyr, :Pca, :Va, :Deoxy]

Q = plot(sol,
         idxs = species_to_plot,             # Only plots the listed species
         lw=2,
         title="9 enzyme cascade",
         xlabel="Time",
         ylabel="Concentration",
         legend = :outerbottom,              # Moves the legend caption below the x-axis
         legend_columns = 4,                 # Arranges legend items in columns to save vertical space
         size = (800, 600),                   # Expands the canvas size so the bottom legend fits comfortably
         )
savefig(Q, "timecourse.pdf")
