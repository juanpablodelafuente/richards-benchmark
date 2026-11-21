# Benchmarking numerical solvers for the 1-D Richards equation

Python implementations for the study *Benchmarking numerical solvers for the 1-D Richards' equation: accuracy, stability and practical guidance for subsurface modelling* by Juan Pablo De la Fuente Cusicanqui, Vassilis Glenis and Chris Kilsby.

## Revised implementation

[`final_solver/`](final_solver/) contains the implementation, two reference resolutions for each benchmark, saved results and figure scripts supplied for manuscript VZJ-2026-05-0062-R. Eight schemes are compared. Its README gives the reproduction commands. The original numerical kernel and archived outputs are preserved in this prepared package.

[`notebooks/`](notebooks/) contains the original implementations, retained for historical comparison. These are not the implementation used for the revised results. Changes include a complete Newton Jacobian, explicit detection of failed iterations, a common boundary treatment, scheme-consistent mass balance calculations and additional solvers. See [`final_solver/VALIDATION_REPORT.md`](final_solver/VALIDATION_REPORT.md) for qualifications that matter when interpreting the outputs.

## Benchmarks

| Benchmark | Revised configuration | Source |
| --- | --- | --- |
| Warrick | Ponded infiltration into a partially wet column, with free drainage at the base. | Warrick, A. W. (2003). *Soil water dynamics*. Oxford University Press. https://doi.org/10.1093/oso/9780195126051.001.0001 |
| Polmann | Infiltration into dry soil with prescribed pressure head at both ends. | Celia, M. A., Bouloutas, E. T., & Zarba, R. L. (1990). A general mass-conservative numerical solution for the unsaturated flow equation. *Water Resources Research, 26*(7), 1483–1496. https://doi.org/10.1029/WR026i007p01483 |
| Miller | Ponding above a hydrostatic initial profile, with a fixed water table at the base. | Miller, C. T., Williams, G. A., Kelley, C. T., & Tocci, M. D. (1998). Robust solution of Richards' equation for nonuniform porous media. *Water Resources Research, 34*(10), 2599–2610. https://doi.org/10.1029/98WR01673 |
| Lehmann | Daily infiltration and evaporation fluxes over initially dry soil, with free drainage. | Lehmann, F., & Ackerer, Ph. (1998). Comparison of iterative methods for improved solutions of the fluid flow equation in partially saturated porous media. *Transport in Porous Media, 31*, 275–292. https://doi.org/10.1023/A:1006555107450 |
| Ireson | A ten-year rainfall record over a freely draining soil column. | Ireson, A. M., Spiteri, R. J., Clark, M. P., & Mathias, S. A. (2023). A simple, efficient, mass-conservative approach to solving Richards' equation (openRE, v1.0). *Geoscientific Model Development, 16*, 659–677. https://doi.org/10.5194/gmd-16-659-2023 |

## Reproduction

Use Python 3.10 or later in an isolated environment. From the repository root, run

```text
python -m venv .venv
```

On Windows Command Prompt, activate it with `.venv\Scripts\activate`. On Linux or macOS, use `source .venv/bin/activate`.

```text
python -m pip install -r final_solver/requirements.txt
cd final_solver
python -m unittest -v test_numerics
python reproduce.py --output reproductions/laptop
```

The new command preserves `results/`, reruns all ordinary configurations, copies the archived references, exports a combined CSV, regenerates Figures 2–15 and records the environment. Add `--recompute-references` to rerun both reference resolutions. Existing output directories are never overwritten. Runtime depends on the machine. Use a different output name for each timing repetition.

The complete repository is needed for the Ireson rainfall and HYDRUS files in `notebooks/ireson/`. The legacy notebook environment in `environment.yml` is separate from the revised solver requirements.

## Computing environment reported in the manuscript

The computational-cost paragraph of the revised manuscript reports an Intel 12th Gen Core i7-1265U processor, 32 GB RAM, 64-bit Windows 10 Enterprise, Python 3.15.2, NumPy 2.5.4 and SciPy 1.18.1. These details were supplied by the author on 20 November 2026 and are recorded in [`final_solver/manuscript_environment.json`](final_solver/manuscript_environment.json).

## Citation and archive

The original notebook archive is **v1.0.1**, DOI https://doi.org/10.5281/zenodo.16806592. Its all-versions DOI is https://doi.org/10.5281/zenodo.16806591. 

## Licence

The revised Python code in `final_solver/`, including the added reproduction and verification utilities, is licensed under the [MIT License](LICENSE).
