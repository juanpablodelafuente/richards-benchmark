# 1D Richards Equation – Benchmarking Numerical Solvers

This repository contains Jupyter notebooks that benchmark six numerical schemes for solving the 1D Richards Equation across five classic test cases. These benchmark tests are well-established in the literature and were selected for their diversity of boundary/initial conditions, flow regimes, and numerical challenges.

---

## 📊 Benchmarks

| Benchmark | Description                    | Methods Included               | Reference |
|----------|-------------------------------|-------------------------------|-----------|
| **Warrick** | Ponded infiltration with abrupt initial conditions | Explicit, Implicit | Warrick et al. (1991), DOI: [10.2136/sssaj1991.03615995005500050006x](https://doi.org/10.1023/B:ENVR.0000046450.62059.62) |
| **Polmann** | Dry initial conditions with rainfall application | All methods | Polmann et al. (1991), DOI: [10.1016/0022-1694(91)90075-F](https://doi.org/10.1016/0022-1694(91)90075-F) |
| **Miller** | Wetting front: constant pressure head ψ = -z | Picard & Newton (ψ and mixed form) | Miller et al. (1998), DOI: [10.1029/98WR01936](https://doi.org/10.1029/98WR01936) |
| **Lehmann** | Transient fluxes over a 2-day time series | Picard (ψ and mixed form) | Lehmann et al. (1998), DOI: [10.1029/97WR03468](https://doi.org/10.1029/97WR03468) |
| **Ireson** | Realistic 10-year rainfall infiltration | Picard (ψ and mixed form) | Ireson et al. (2006), DOI: [10.1016/j.jhydrol.2005.11.043](https://doi.org/10.1016/j.jhydrol.2005.11.043) |

Each benchmark tests different aspects of numerical performance (nonlinearity, mass conservation, convergence) and provides a robust basis for comparing solvers.

---

## 📁 Structure

- `notebooks/` – Organised by benchmark
- `results/` – Placeholder folders for output figures/tables
- `environment.yml` – Reproducible conda environment
- `.gitignore` – Prevents tracking of auto-generated files

---

## 🚀 Getting Started

To run the notebooks locally:

```bash
conda env create -f environment.yml
conda activate richards-benchmark
jupyter lab
```

---

## 📌 Notes

- All solvers are implemented in Python and benchmarked using consistent initial/boundary conditions.
- Numerical methods include explicit, semi-implicit (Picard), and fully implicit (Newton) approaches.
- A focus is placed on modular implementation and transparency of source code.

---

## 📄 License

MIT License

---

## 🤝 Contributions

Pull requests and feedback are welcome. Please open an issue if you have suggestions for improvements or additional test cases.
