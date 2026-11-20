# Revised Richards equation benchmarks

This directory contains the implementation, reference solutions, results and figures for *Benchmarking numerical solvers for the 1-D Richards' equation: accuracy, stability and practical guidance for subsurface modelling* (VZJ-2026-05-0062-R). Eight schemes are compared across the Warrick, Polmann, Miller, Lehmann and Ireson benchmarks. The supplied results are retained as the manuscript archive. Reproduction tools write to a separate directory.

## Contents

| File or directory | Purpose |
| --- | --- |
| `richards_revised.py` | Hydraulic functions, grids, face fluxes, solvers, stopping criteria, mass balance and profile errors. |
| `run_all.py` | Benchmark configurations and reference definitions. Original commands reuse cached results. |
| `reproduce.py` | Safe reproduction, environment recording, comparisons, CSV export and figures. |
| `test_numerics.py` | Six checks of retention derivatives, maximum capacity, Newton Jacobians, the L update, conservation and agreement of converged mixed solutions. |
| `make_figures.py` | Figures 2–15 from saved profiles and summaries. |
| `verify.py` | Selected diagnostic comparisons with original notebooks. Prints differences without pass/fail assertions. |
| `results/` | Supplied reference and ordinary runs as JSON/NPZ pairs, plus summaries. |
| `tables/all_results.csv` | Supplied combined table of 109 rows. |
| `figures/` | Supplied Figures 1–15. Figure 1 is a separately supplied schematic. |
| `ARCHIVE_NOTES.md` | Numerical conventions, limitations and manuscript clarifications. |
| `manuscript_environment.json` | Computing environment reported in the manuscript supplied by the author on 20 November 2026. |

## Reproduction

Install `requirements.txt` in an isolated Python environment and run from this directory

```text
python -m unittest -v test_numerics
python reproduce.py --output reproductions/laptop
```

The new directory contains results, `tables/all_results.csv`, Figures 2–15, `environment.json`, `requirements-measured.txt` and `comparison.json`. Reference files are copied and hashed unless `--recompute-references` is selected.

```text
python reproduce.py --output reproductions/full --recompute-references
python reproduce.py --output reproductions/polmann --cases polmann --no-figures
```

Existing output directories cannot be overwritten. Preserve the supplied archive until the new results are checked. References and L-scheme runs may dominate runtime. No fixed completion time is promised.

The environment record includes Python, NumPy, SciPy, Matplotlib, operating system, processor where available, NumPy build information, thread settings, source hashes and input hashes. `requirements.txt` specifies minimum versions. The manuscript's reported versions are recorded separately in `manuscript_environment.json`. `requirements-measured.txt` records the packages actually used in a reproduction; it is not a complete operating-system or BLAS lock.

The original low-level commands remain available

```text
python run_all.py polmann refs
python run_all.py polmann runs
python run_all.py polmann summ
python make_figures.py fig9
```

These skip cached runs and write into supplied results or figures. Use `reproduce.py` for a fresh timing exercise. `summ` alone does not regenerate the combined CSV.

## Interpretation

Numerical outputs should agree within justified tolerances for fixed algorithms and settings. Bit-for-bit equality is not guaranteed across platforms or package versions. Small differences near stopping thresholds may change iteration counts. The comparison tool flags changes and checks completion status and final time separately. Its tolerances are regression diagnostics, not estimates of discretisation error.

Failed runs are not final solutions. `completed` only means the scheduled integration ended; explicit water content can still exceed saturation or oscillate.

## Computational cost

The following environment was used for the complete simulations.

| Component | Reported value |
| --- | --- |
| Processor | Intel 12th Gen Core i7-1265U |
| RAM | 32 GB |
| Operating system | Windows 10 Enterprise, 64-bit |
| Python | 3.15.2 |
| NumPy | 2.5.4 |
| SciPy | 1.18.1 |

These author-supplied details are recorded in `manuscript_environment.json`. They are distinct from the automatically recorded validation environment in `validation/environment.json`. The supplied manuscript runtimes remain unchanged. 

For any new timing exercise, record the environment used for that run. Compare timings from the same machine and session design. Run serially without other heavy work; repeat very short configurations if their ranking is discussed.

## Licence

The revised Python code and added reproduction and verification utilities use the [MIT License](../LICENSE). See the repository README for the scope and treatment of other material.
