# Proposed v2.0.0 release

## Revised solver and results for VZJ-2026-05-0062-R

This release adds the revised implementation, reference solutions, saved results and figures for the comparative study of numerical solvers for the one-dimensional Richards equation. It includes explicit and non-iterative implicit schemes, Picard and Newton iterations for the pressure head and mixed forms, the L-scheme and an L/Newton combination across five benchmarks. The original notebooks remain available for comparison.

The framework uses a complete Newton Jacobian, explicit reporting of failed iterations, scheme-consistent mass balance calculations, a common banded linear solver and two reference resolutions per benchmark. Reproduction preserves supplied results and records the computing environment. The README and archive notes explain numerical conventions and limitations.

Before publishing, resolve the licence decision, finalise timing provenance and review the validation report. This file prepares a release; version 2.0.0 has not been published.
