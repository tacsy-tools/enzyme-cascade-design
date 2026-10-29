# Reject unsupported runtimes before importing the pinned package environment.
function require_julia_version(version=VERSION)
    if version.major != 1 || version.minor != 11
        error("This environment requires Julia 1.11.x; found $version. " *
              "With juliaup, run `juliaup add 1.11.5` and " *
              "`juliaup override set 1.11.5` in code/.")
    end
end

require_julia_version()
