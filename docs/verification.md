# Verification

Checked on **28 October 2026**, using the repository's pinned Julia environment
and an installed Python/MØD environment. The checks
ran from this separate repository checkout, using its bundled model inputs.
They do not represent an independent installation on another machine.

| Check | Result |
| --- | --- |
| Python interface tests | All 10 passed, including runtime checks |
| 9MEC kinetic batch | All 50 cases recomputed; product endpoints match the supplied results exactly |
| Saved pathway results | All 14 records can be displayed with Python alone |
| Fresh clone | Reference and four-branchpoint comparison run without private code; product endpoints match exactly |
| Independent 9MEC derivative calculation | 49 probes, including zero-species boundaries; maximum error 5.69 × 10⁻¹⁴ |
| Generated/reference 9MEC trajectories | Maximum absolute difference 3.20 × 10⁻¹⁴ |
| Native Michaelis–Menten tutorial | Two activity settings; maximum integrated-equation residual 9.40 × 10⁻¹¹ |
| 9MEC MØD rebuild | 39 species / 19 reactions; native reload, carbon counts and stoichiometries match |
| Seven-round 3HP MØD rebuild | 83 species / 248 reactions; native reload, carbon counts and stoichiometries match |
| Editable kinetic tables | Rebuilding reproduces the supplied species, reactions, rate laws and time settings |

The kinetic runner checks successful completion, the requested endpoint,
finite/nonnegative sampled states, conserved pools and agreement at two numerical
tolerances. The generated MM tutorial is also checked against its integrated
rate equation by `audit_results.py`.

The 50 9MEC cases contain 46 distinct enzyme settings; repeated reference settings
provide consistency checks. The generic native-model tutorial supplies an executable example of the model
interface, checked against the integrated Michaelis–Menten equation.

[`verification.json`](verification.json) records numerical checks.
[`models.json`](models.json) identifies the principal inputs by SHA256.
Full trajectories and numerical check files are generated when examples are rerun.

## Runtime checks

Rechecked on **29 October 2026** with Julia **1.11.5**. The Python entry points
reject unsupported Julia versions before preparing outputs, and Julia entry
points check the runtime before loading packages. Input preparation without
integration continues to work with Python alone.

The two-case enzyme comparison retains exactly the supplied product endpoints.
The 49 independent derivative probes and reference-model comparison also pass.
The compatibility range is restricted to Julia 1.11.x; pinned package versions
and scientific model inputs are unchanged.
