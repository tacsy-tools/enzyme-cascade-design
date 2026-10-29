# Generated from the JSON input; edit the input, then regenerate.
# Reject unsupported runtimes before importing the pinned package environment.
function require_julia_version(version=VERSION)
    if version.major != 1 || version.minor != 11
        error("This environment requires Julia 1.11.x; found $version. " *
              "With juliaup, run `juliaup add 1.11.5` and " *
              "`juliaup override set 1.11.5` in code/.")
    end
end

require_julia_version()

using Catalyst
using DifferentialEquations
using DelimitedFiles

MM00(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E) / ( (km * (1 + (I1 / ki1))) + (S * (1 + (I2 / ki2))) )
MM01(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E) / ( (km * (1 + (I1 / ki1) + (I2 / ki2))) + S )
MM03(E, kcat, km, S1, S2) = (kcat * E) / ( (km * km) + (km * S1) + (km * S2) + (S1 * S2) )
MM14(E, kcat, km, S, I1, ki1, I2, ki2) = (kcat * E) / ((km * (1 + (I1 / ki1))) + (S * (1 + (I2 / ki2))))
MM17(E, kcat, km, S) = (kcat * E) / (km + S)
MM18(E, kcat, km, S, I1, ki1) = (kcat * E) / ((km * (1 + (I1 / ki1))) + S)

rn = @reaction_network begin
    # r39: MM00
    MM00(r39_E, r39_kcat, r39_km, Dhq, r39_I1, r39_ki1, r39_I2, r39_ki2), Dhq --> Dhs + H2O
    # r40: MM01
    MM01(r40_E, r40_kcat, r40_km, Dhs, Dhq, r40_ki1, Skm, r40_ki2), Dhs + Nadh + H_plus --> Skm + Nad_plus
    # r41: MM18
    MM18(r41_E, r41_kcat, r41_km, Skm, Atp, r41_ki1), Skm + Atp --> S3p + Adp
    # r42: MM03
    MM03(r42_E, r42_kcat, r42_km, S3p, Pep), S3p + Pep --> Epsp + Pi
    # r43: MM18
    MM18(r43_E, r43_kcat, r43_km, Epsp, Nadh, r43_ki1), Epsp --> Pi + Cha
    # r44: MM03
    MM03(r44_E, r44_kcat, r44_km, Cha, Gln), Cha + Gln --> Glu + Adc
    # r45: MM14
    MM14(r45_E, r45_kcat, r45_km, Adc, r45_I1, r45_ki1, r45_I2, r45_ki2), Adc --> Pyr + AmBez
    # r46: MM14
    MM14(r46_E, r46_kcat, r46_km, AmBez, r46_I1, r46_ki1, r46_I2, r46_ki2), Nadh + H_plus + O2 + AmBez --> Nad_plus + CO2 + H2O + AmPhOH
    # r47: MM14
    MM14(r47_E, r47_kcat, r47_km, AmPhOH, r47_I1, r47_ki1, r47_I2, r47_ki2), AcCoA + AmPhOH --> CoA + Apap
    # r48: MM17
    MM17(r48_E, r48_kcat, r48_km, Cha), Cha --> Iso
    # r49: MM17
    MM17(r49_E, r49_kcat, r49_km, Iso), Iso --> Pyr + Sal
    # r50: MM17
    MM17(r50_E, r50_kcat, r50_km, Cha), Cha --> Ppa
    # r51: MM17
    MM17(r51_E, r51_kcat, r51_km, Ppa), Nad_plus + Ppa --> Nadh + H_plus + CO2 + Hpp
    # r52: MM03
    MM03(r52_E, r52_kcat, r52_km, Hpp, HTD), Hpp + HTD --> Imz + Tyr
    # r53: MM14
    MM14(r53_E, r53_kcat, r53_km, Dhs, r53_I1, r53_ki1, r53_I2, r53_ki2), Dhs --> H2O + Pca
    # r54: MM17
    MM17(r54_E, r54_kcat, r54_km, Pca), Sam + Pca --> Sah + Va
    # r55: MM17
    MM17(r55_E, r55_kcat, r55_km, Adp), 2*Adp --> Atp + Amp
    # r56: MM17
    MM17(r56_E, r56_kcat, r56_km, Deoxy), Deoxy --> Dhq + Pi
    # r57: MM18
    MM18(r57_E, r57_kcat, r57_km, E4p, Pep, r57_ki1), Pep + E4p + H2O --> Deoxy + Pi
end

u0 = [
    :Dhq => 1.0,
    :Dhs => 0.0,
    :Nadh => 2.0,
    :H_plus => 1.0,
    :Skm => 0.0,
    :Nad_plus => 0.0,
    :Atp => 2.0,
    :S3p => 0.0,
    :Adp => 0.0,
    :Amp => 0.0,
    :Pep => 1.5,
    :E4p => 1.0,
    :Epsp => 0.0,
    :Deoxy => 0.0,
    :Pi => 0.0,
    :Cha => 0.0,
    :CO2 => 0.0,
    :H2O => 10.0,
    :O2 => 1.0,
    :Sam => 1.0,
    :Sah => 0.0,
    :Va => 0.0,
    :CoA => 0.0,
    :AcCoA => 1.0,
    :Iso => 0.0,
    :Pyr => 0.0,
    :Ppa => 0.0,
    :Sal => 0.0,
    :Gln => 1.0,
    :Glu => 0.0,
    :Adc => 0.0,
    :AmBez => 0.0,
    :AmPhOH => 0.0,
    :Apap => 0.0,
    :Hpp => 0.0,
    :HTD => 1.0,
    :Imz => 0.0,
    :Tyr => 0.0,
    :Pca => 0.0,
]

p = [
    :r39_E => 0.2,
    :r39_kcat => 3.2,
    :r39_km => 0.02,
    :r39_I1 => 0.0,
    :r39_ki1 => 1.0,
    :r39_I2 => 0.0,
    :r39_ki2 => 1.0,
    :r40_E => 0.2,
    :r40_kcat => 0.405,
    :r40_km => 0.287,
    :r40_ki1 => 0.42,
    :r40_ki2 => 0.14,
    :r41_E => 0.2,
    :r41_kcat => 30.8,
    :r41_km => 0.2,
    :r41_ki1 => 0.5,
    :r42_E => 0.2,
    :r42_kcat => 8.6,
    :r42_km => 0.1,
    :r43_E => 0.2,
    :r43_kcat => 0.8,
    :r43_km => 0.0027,
    :r43_ki1 => 0.043,
    :r44_E => 0.2,
    :r44_kcat => 0.00544,
    :r44_km => 0.0016,
    :r45_E => 0.2,
    :r45_kcat => 1.5,
    :r45_km => 0.015,
    :r45_I1 => 0.0,
    :r45_ki1 => 1.0,
    :r45_I2 => 0.0,
    :r45_ki2 => 2.0,
    :r46_E => 0.2,
    :r46_kcat => 0.98,
    :r46_km => 0.02,
    :r46_I1 => 0.0,
    :r46_ki1 => 1.0,
    :r46_I2 => 0.0,
    :r46_ki2 => 2.0,
    :r47_E => 0.2,
    :r47_kcat => 18.68,
    :r47_km => 2.22,
    :r47_I1 => 0.0,
    :r47_ki1 => 1.0,
    :r47_I2 => 0.0,
    :r47_ki2 => 2.0,
    :r48_E => 0.2,
    :r48_kcat => 0.67,
    :r48_km => 0.007,
    :r49_E => 0.2,
    :r49_kcat => 0.035,
    :r49_km => 0.0026,
    :r50_E => 0.2,
    :r50_kcat => 1.995,
    :r50_km => 1.14,
    :r51_E => 0.2,
    :r51_kcat => 0.655,
    :r51_km => 0.25,
    :r52_E => 0.2,
    :r52_kcat => 428.4,
    :r52_km => 0.42,
    :r53_E => 0.2,
    :r53_kcat => 153.7,
    :r53_km => 0.311,
    :r53_I1 => 0.0,
    :r53_ki1 => 1.0,
    :r53_I2 => 0.0,
    :r53_ki2 => 2.0,
    :r54_E => 0.2,
    :r54_kcat => 0.032,
    :r54_km => 0.015,
    :r55_E => 0.2,
    :r55_kcat => 783.0,
    :r55_km => 0.35,
    :r56_E => 0.2,
    :r56_kcat => 16.0,
    :r56_km => 0.0057,
    :r57_E => 0.2,
    :r57_kcat => 21.83,
    :r57_km => 0.037,
    :r57_ki1 => 0.015,
]
tspan = (0.0, 1000.0)
problem = ODEProblem(rn, u0, tspan, p)

# Including this file exposes rn, u0, p, and problem for further analysis.
if abspath(PROGRAM_FILE) == @__FILE__
    times = range(tspan[1], tspan[2]; length=201)
    solution = solve(problem, Rosenbrock23(); saveat=times, reltol=1e-8, abstol=1e-10)
    SciMLBase.successful_retcode(solution) || error("ODE solve failed: $(solution.retcode)")
    output = isempty(ARGS) ? splitext(@__FILE__)[1] * ".csv" : ARGS[1]
    header = ["time"; string.(species(rn))]
    data = hcat(solution.t, permutedims(Array(solution)))
    writedlm(output, vcat(permutedims(header), data), ',')
    println("Saved ", output, "; solver status: ", solution.retcode)
end
