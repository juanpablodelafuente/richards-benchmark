# Proposed v2.0.0 release

## Revised solver and results for VZJ-2026-05-0062-R

This release adds the revised implementation, reference solutions, saved results and figures for the comparative study of numerical solvers for the one-dimensional Richards equation. It includes explicit and non-iterative implicit schemes, Picard and Newton iterations for the pressure head and mixed forms, the L-scheme and an L/Newton combination across five benchmarks. The implementation is in `final_solver/`. The original notebooks remain available for comparison.

The framework uses a complete Newton Jacobian, explicit reporting of failed iterations, scheme-consistent mass balance calculations, a common banded linear solver and two reference resolutions per benchmark. Reproduction preserves supplied results and records the computing environment. The README and validation report explain numerical conventions and limitations.

The revised Python code is licensed under MIT. The manuscript reports timings on an Intel 12th Gen Core i7-1265U with 32 GB RAM, 64-bit Windows 10 Enterprise, Python 3.15.2, NumPy 2.5.4 and SciPy 1.18.1. These details are recorded in `final_solver/manuscript_environment.json`; the independent validation environment is recorded separately.

Review the validation report and final manuscript before publishing. This file prepares a release; version 2.0.0 has not been published.
