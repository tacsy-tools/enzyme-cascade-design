using Catalyst, DifferentialEquations, DelimitedFiles

out = abspath(ARGS[1])
include(joinpath(out, "model.jl"))
generated = problem
generated_names = replace.(string.(species(rn)), "(t)" => "")
states, header = readdlm(joinpath(out, "states.csv"), ',', Float64; header=true)
expected, _ = readdlm(joinpath(out, "expected.csv"), ',', Float64; header=true)
order = [only(findall(==(name), string.(vec(header)))) for name in generated_names]
maximum_error = 0.0
for index in axes(states, 1)
    derivative = zeros(length(order))
    generated.f(derivative, states[index, order], generated.p, 0.0)
    @assert isapprox(derivative, expected[index, order]; rtol=1e-11, atol=1e-11)
    global maximum_error = max(maximum_error, maximum(abs.(derivative - expected[index, order])))
end

# Load only the reference model, stopping before its plotting/integration tail.
source = joinpath(@__DIR__, "examples/9mec/source/9MAC03.jl")
reference = Module(gensym(:ReferenceModel))
Core.eval(reference, :(using Catalyst, DifferentialEquations))
finished = Ref(false)
function model_only(expression)
    finished[] && return nothing
    expression isa Expr && expression.head == :using && return nothing
    if expression isa Expr && expression.head == :(=) && expression.args[1] == :oprob
        finished[] = true
    end
    return expression
end
Base.include(model_only, reference, source)
original = reference.oprob
original_names = replace.(replace.(string.(species(reference.rn)), "(t)" => ""), "Htd" => "HTD")
permutation = [only(findall(==(name), original_names)) for name in generated_names]
times = range(0.0, 1000.0; length=201)
a = solve(generated, Rosenbrock23(); saveat=times, reltol=1e-9, abstol=1e-14)
b = solve(original, Rosenbrock23(); saveat=times, reltol=1e-9, abstol=1e-14)
@assert SciMLBase.successful_retcode(a) && SciMLBase.successful_retcode(b)
trajectory_error = maximum(abs.(Array(a) - Array(b)[permutation, :]))
@assert trajectory_error < 1e-7
message = "PASS: $(size(states, 1)) independent derivative probes; max error=$maximum_error\n" *
          "PASS: original/generated trajectory; max error=$trajectory_error\n"
write(joinpath(out, "checks.txt"), message)
print(message)
