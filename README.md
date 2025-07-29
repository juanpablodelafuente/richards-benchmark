# 1D Richards Equation – Benchmarking Numerical Solvers

This repository contains Jupyter notebooks that benchmark six numerical schemes for solving the 1D Richards Equation across five classic test cases.

### Benchmarks
| Benchmark | Description                     | Methods Included                |
|-----------|---------------------------------|----------------------------------|
| Warrick   | Ponded infiltration              | Explicit, Implicit               |
| Polmann   | Dry start                        | All methods                      |
| Miller    | Wetting front, ψ = -z            | Picard & Newton (ψ and mixed)    |
| Lehmann   | Flux time series                 | Picard (ψ and mixed)             |
| Ireson    | 10-year rainfall                 | Picard (ψ and mixed)             |

### Structure
- `notebooks/`: Organised by benchmark
- `results/`: Placeholder folders for figures and tables
- `environment.yml`: Reproducible conda environment
- `.gitignore`: Prevents saving of auto-generated files

### Getting Started
To run the notebooks locally:

```bash
conda env create -f environment.yml
conda activate richards-benchmark
jupyter lab
```

### License
MIT License
