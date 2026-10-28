# The analytical MM tutorial through the native-model input interface.
using Catalyst, DifferentialEquations

function build_case(config, spec)
    rn = @reaction_network begin
        @parameters activity vmax km
        activity*vmax*S/(km+S), S => P
    end
    factor = Float64(spec["activity"])
    isfinite(factor) && factor > 0 || error("Activity must be finite and positive")
    problem = ODEProblem(rn, [:S=>2.0, :P=>0.0],
        (0.0, Float64(config["end_time"])), [:activity=>factor, :vmax=>3.0, :km=>1.0])
    return (;rn, problem, products=String.(config["products"]), pools=[["S","P"]],
        events=Float64[], extra_names=["activity_factor"], extra=(sol,t)->[factor],
        event_check=sol->nothing)
end
