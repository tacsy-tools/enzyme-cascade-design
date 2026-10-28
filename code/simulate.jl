# Integrate prepared cases through the common numerical checking kernel.
include("simulation_common.jl")

function run_batch(model, directory)
    original = model.problem
    names = species_names(model.rn)
    index(name) = only(findall(==(name), names))
    products = readlines(joinpath(directory, "products.txt"))
    indices = index.(products)
    pools = [split(line, ',') for line in readlines(joinpath(directory, "pools.txt")) if !isempty(line)]
    cases, header = readdlm(joinpath(directory, "cases.csv"), ',', Any; header=true)
    mapping, _ = readdlm(joinpath(directory, "parameters.csv"), ',', Any; header=true)
    enzymes = string.(vec(header)[2:end])
    keys = isempty(enzymes) ? Symbol[] : Symbol.(string.(mapping[:, 2]))
    @assert isempty(enzymes) || string.(mapping[:, 1]) == enzymes
    rows, checks, states = Vector{Any}[], Vector{Any}[], Vector{Any}[]
    times = range(original.tspan[1], original.tspan[2]; length=201)
    function integrate(problem, rtol, atol)
        _, data = solve_checked(problem, names, times, pools; rtol=rtol, atol=atol)
        return data
    end
    for row in eachrow(cases)
        name = string(row[1])
        factors = parse.(Float64, string.(row[2:end]))
        problem = remake(original; p=deepcopy(original.p), u0=copy(original.u0))
        expected = Dict(key => original.ps[key] * factor for (key, factor) in zip(keys, factors))
        for (key, value) in expected
            problem.ps[key] = value
        end
        @assert all(problem.ps[key] == get(expected, key, value) for (key, value) in model.p)
        @assert all(original.ps[key] == value for (key, value) in model.p)
        @assert problem.u0 == original.u0 && problem.tspan == original.tspan
        coarse = integrate(problem, 1e-9, 1e-14)
        fine = integrate(problem, 1e-11, 1e-16)
        final = fine[indices, end]
        error = maximum(abs.(final - coarse[indices, end]) ./ max.(abs.(final), 1e-12))
        @assert error < 1e-3 "Endpoint convergence failed for $name: $error"
        push!(rows, [name; factors; final])
        push!(states, [name; fine[:, end]])
        push!(checks, [name, "Success", error, minimum(fine), 1e-11, 1e-16])
        data = hcat(collect(times), permutedims(fine))
        writedlm(joinpath(directory, "trajectory-$(length(rows)).csv"),
                 vcat(permutedims(["time"; names]), data), ',')
        println(basename(directory), ": ", name, "; convergence=", error)
        flush(stdout)
    end
    writedlm(joinpath(directory, "endpoints.csv"),
             vcat(permutedims(["case"; enzymes; products]), permutedims(hcat(rows...))), ',')
    writedlm(joinpath(directory, "final-states.csv"),
             vcat(permutedims(["case"; names]), permutedims(hcat(states...))), ',')
    check_header = ["case", "status", "maximum_relative_endpoint_difference",
                    "minimum_sampled_concentration", "reltol", "abstol"]
    writedlm(joinpath(directory, "checks.csv"),
             vcat(permutedims(check_header), permutedims(hcat(checks...))), ',')
    write_runtime(directory)
end

isempty(ARGS) && error("Usage: simulate.jl RUN_DIRECTORY ... | --native CONFIG.toml OUTPUT")
if first(ARGS) == "--native"
    length(ARGS) == 3 || error("Usage: simulate.jl --native CONFIG.toml OUTPUT")
    config_path = abspath(ARGS[2])
    config = TOML.parsefile(config_path)
    model = Module(gensym(:NativeModel))
    Base.include(model, joinpath(dirname(config_path), config["model"]))
    Base.invokelatest(run_native, model, config_path, abspath(ARGS[3]))
else
    for argument in ARGS
        directory = abspath(argument)
        batch_model = Module(gensym(:DesignModel))
        Base.include(batch_model, joinpath(directory, "model.jl"))
        Base.invokelatest(run_batch, batch_model, directory)
    end
end
