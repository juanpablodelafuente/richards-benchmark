# Validation report

Assessment completed on 19 November 2026 against the supplied `revised_solver.zip` and GitHub commit `222c73a344592c4e3049b7b4e0fa1bf8cd702161`.

## Results

All 103 ordinary run configurations and all ten reference runs were independently executed. All saved arrays (`z`, `psi`, `theta`, `daily_S`) matched the supplied arrays exactly, including the location of NaN entries in failed runs. All per-run JSON fields other than runtime also matched exactly, including completion/failure status, final time, iteration counts, mass balance and failure reasons.

| Benchmark | Configurations including two references | Completed | Failed | Numerical comparison |
| --- | --- | --- | --- | --- |
| Warrick | 22 | 22 | 0 | Exact match |
| Polmann | 36 | 33 | 3 | Exact match |
| Miller | 31 | 13 | 18 | Exact match |
| Lehmann | 15 | 8 | 7 | Exact match |
| Ireson | 9 | 9 | 0 | Exact match |

The 28 failures are reproduced benchmark outcomes, not failures of the reproduction process. `completed` is a termination status and does not establish physical admissibility or stability. In particular, the two oscillatory Warrick explicit results exceed saturation, as documented in `ARCHIVE_NOTES.md`.

All 109 supplied combined-CSV rows agree with their summary JSON values. Recomputing the profile errors from the supplied NPZ files reproduces the summary errors. The new reproduction exported a combined CSV and regenerated Figures 2–15 successfully. Figure 1 has no generating script in this package. A visual check of the regenerated Figure 9 showed crowded annotations for closely spaced points; these should be checked in the final publication layout. All-figure execution is not a claim of a complete visual audit of the final manuscript PDF.

The supplemental Polmann explicit run at 50 s failed after two accepted steps, at t = 100 s. Its metadata are retained in `validation/polmann_50s.json` and its repeatable command is `check_polmann_50s.py`.

## Equation checks

All six tests in `test_numerics.py` passed.

- Retention derivatives agree with finite differences in unsaturated soil.
- The analytic maximum capacity agrees with a dense sampling check.
- Complete Newton matrices agree with independent residual perturbations for both equation forms, on prescribed head and flux grids, away from the saturation switch.
- A single L update satisfies its stabilised mixed equation.
- Summed flux divergences give the discrete mass balance identity.
- Picard, Newton and L/Newton give matching converged mixed solutions in the tested Polmann configuration.

These tests verify specific algebraic properties. They do not prove global convergence, establish stability for untested time steps, or validate the physical benchmark data. Reference reruns use the same kernel as the ordinary runs, so they test reproducibility and refinement consistency, not independence from shared implementation errors.

## Environment

The independent reproduction used Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 and Matplotlib 3.10.8 on an INTEL(R) XEON(R) PLATINUM 8573C. The full operating-system, build, thread and hash record is in `validation/environment.json`.

These are validation measurements in the execution environment. They are not measurements on the author's laptop and are not adopted manuscript runtimes. Other assessment work was performed during the overall validation session, and timings were not repeated to estimate variability. The original package's runtime environment remains unknown.

Exact agreement was observed in this reproduction. It is not a guarantee of exact agreement on every other platform or software version. `reproduce.py` therefore records and flags differences for inspection rather than assuming only runtime can change.

## Files preserved

252 supplied files other than the revised README were checked and preserved byte for byte, including the numerical kernel, original run and plotting scripts, requirements, all results, the combined CSV and figures. `archived_checksums.sha256` records their hashes. Original GitHub notebooks and input files are unchanged. Additional reproduction tools and documentation are separate.

## Items to reconcile before publication

1. Define the RMSE sum over the actual stored unknowns. Interior vertex-grid weights sum to H − Δz, while cell-grid weights sum to H.
2. Make the manuscript's storage sum match the evolved unknowns and numerical boundary faces.
3. Disclose the small positive saturated capacity in the pressure head formulations and modified Picard iteration matrix.
4. Describe the bounded backtracking faithfully. Its minimum-factor update is not guaranteed to satisfy the sufficient-decrease test.
5. Treat explicit oversaturation as an inadmissible comparison outcome. Interpret failure counters as accepted-step information, with the documented dummy entry at first-step failure.
6. Confirm the licence and timing provenance, then check the final PDF and response letter against the chosen archived version.

Most of these are specific documentation corrections if the supplied numerical implementation is retained. If the storage convention, saturated capacity or line-search acceptance rule is changed, a new checked numerical run is needed. Suggested manuscript wording and exact functions are in `ARCHIVE_NOTES.md`.

## Access and release status

During initial preparation, the GitHub repository was readable but creating a branch returned HTTP 403, `Resource not accessible by integration`, and a normal Git push lacked authenticated credentials. After the repository authorisation was updated on 19 November 2026, write access was verified by creating `prepare-v2-archive`. This branch contains the preparation for review. No release, Zenodo record or ORCID account has been published or changed by this preparation.

The existing Zenodo public metadata identify DOI `10.5281/zenodo.16806592` as v1.0.1, with concept DOI `10.5281/zenodo.16806591`, creator `JP_delaf` and licence CC BY 4.0. The previous GitHub README stated MIT without a licence file. This conflict needs an author decision before a new licence is adopted.

No new manuscript PDF accompanied the uploaded solver ZIP. The scientific wording checks used the previously available `Manuscript_VZJ-2026-05-0062-R(2).docx`. They cannot certify the contents or line numbers of a newer PDF.
