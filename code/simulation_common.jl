# Shared integration and checks for generated and native Catalyst models.
include("julia_runtime.jl")
using Catalyst, DifferentialEquations, DelimitedFiles, TOML, SHA

species_names(rn) = replace.(string.(species(rn)), "(t)" => "")

function solve_checked(problem, names, times, pools;
                       solver=Rosenbrock23(), rtol=1e-9, atol=1e-14,
                       events=Float64[])
    solution = solve(problem, solver; saveat=times, dense=false,
                     reltol=rtol, abstol=atol, tstops=events)
    @assert SciMLBase.successful_retcode(solution) solution.retcode
    @assert last(solution.t) == problem.tspan[2] "Requested endpoint not reached"
    data = Array(solution)
    @assert all(isfinite, data) && minimum(data) >= -1e-9
    for pool in pools
        indices = [only(findall(==(name), names)) for name in pool]
        total = vec(sum(data[indices, :]; dims=1))
        @assert maximum(abs.(total .- total[1])) < 1e-8
    end
    return solution, data
end

function write_runtime(directory)
    versions = "Julia=$(VERSION)\nCatalyst=$(pkgversion(Catalyst))\n" *
               "DifferentialEquations=$(pkgversion(DifferentialEquations))\n"
    write(joinpath(directory, "runtime.txt"), versions)
end

function run_native(model, config_path, directory)
    config = TOML.parsefile(config_path)
    duration = config["end_time"]
    points = config["save_points"]
    isfinite(duration) && duration > 0 || error("Expected positive finite duration")
    points isa Integer && points >= 2 || error("Expected at least two samples")
    isempty(config["cases"]) && error("At least one case is required")
    case_names = [case["name"] for case in config["cases"]]
    length(unique(case_names)) == length(case_names) || error("Duplicate case names")
    for name in case_names
        if isempty(name) || any(value -> occursin(value, name), [",", "\n", "\r"])
            error("Invalid case name")
        end
    end
    algorithms = Dict("TRBDF2" => TRBDF2, "Tsit5" => Tsit5)
    solver_name = get(config, "solver", "TRBDF2")
    haskey(algorithms, solver_name) || error("Unknown solver: $solver_name")
    solver = algorithms[solver_name]()
    isdir(directory) && !isempty(readdir(directory)) && error("Use a new empty output directory")
    mkpath(directory)

    # Preserve the explicitly declared model inputs with each calculation.
    input = joinpath(directory, "input")
    mkpath(input)
    files = unique([config["model"]; get(config, "includes", String[]); basename(config_path)])
    for name in files
        isabspath(name) && error("Model input paths must be relative to the TOML file")
        any(==(".."), splitpath(name)) && error("Model inputs must stay in the configuration directory")
        destination = joinpath(input, name)
        mkpath(dirname(destination))
        cp(joinpath(dirname(config_path), name), destination; force=true)
    end

    rows, states, checks = Vector{Any}[], Vector{Any}[], Vector{Any}[]
    names = String[]
    for (index, spec) in enumerate(config["cases"])
        case = model.build_case(config, spec)
        names = species_names(case.rn)
        @assert case.products == String.(config["products"]) "Product selection differs from configuration"
        indices = [only(findall(==(name), names)) for name in case.products]
        times = sort(unique([collect(range(case.problem.tspan...; length=points)); case.events]))
        _, coarse = solve_checked(case.problem, names, times, case.pools;
                                  solver=solver, rtol=1e-8, atol=1e-12, events=case.events)
        solution, fine = solve_checked(case.problem, names, times, case.pools;
                                       solver=solver, rtol=1e-10, atol=1e-14, events=case.events)
        case.event_check(solution)
        final = fine[indices, end]
        relative = maximum(abs.(final - coarse[indices, end]) ./ max.(abs.(final), 1e-8))
        scaled = maximum(abs.(fine[:, end] - coarse[:, end]) ./
                         (1e-7 .+ 1e-5 * abs.(fine[:, end])))
        @assert scaled < 1 "Endpoint tolerance convergence failed for $(spec["name"]): $scaled"
        push!(rows, [spec["name"]; final])
        push!(states, [spec["name"]; fine[:, end]])
        push!(checks, [spec["name"], "Success", relative, minimum(fine),
                       1e-10, 1e-14, scaled, last(solution.t)])
        extra = permutedims(hcat([case.extra(solution, time) for time in solution.t]...))
        @assert all(isfinite, extra)
        header = permutedims(["time"; names; case.extra_names])
        data = hcat(solution.t, permutedims(fine), extra)
        writedlm(joinpath(directory, "trajectory-$index.csv"), vcat(header, data), ',')
        println(basename(directory), ": ", spec["name"], "; tolerance check=", scaled)
        flush(stdout)
    end
    products = String.(config["products"])
    writedlm(joinpath(directory, "endpoints.csv"),
             vcat(permutedims(["case"; products]), permutedims(hcat(rows...))), ',')
    writedlm(joinpath(directory, "final-states.csv"),
             vcat(permutedims(["case"; names]), permutedims(hcat(states...))), ',')
    check_header = ["case", "status", "maximum_relative_endpoint_difference",
                    "minimum_sampled_concentration", "reltol", "abstol",
                    "maximum_scaled_state_endpoint_difference", "last_time"]
    writedlm(joinpath(directory, "checks.csv"),
             vcat(permutedims(check_header), permutedims(hcat(checks...))), ',')
    manifest = Dict(
        "products" => products,
        "cases" => config["cases"],
        "units" => config["units"],
        "interpretation" => config["interpretation"],
        "input_format" => "native Catalyst + TOML",
        "time" => Dict("end" => duration, "save_points" => points),
        "inputs" => Dict(name => bytes2hex(sha256(read(joinpath(input, name)))) for name in files),
        "solver" => "$solver_name; two tolerances; endpoint error <= 1e-7 + 1e-5*abs(fine)",
    )
    open(joinpath(directory, "manifest.toml"), "w") do io
        TOML.print(io, manifest; sorted=true)
    end
    write_runtime(directory)
end
