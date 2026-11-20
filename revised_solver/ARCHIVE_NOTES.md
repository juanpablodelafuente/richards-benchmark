# Numerical and archive notes

The numerical kernel and supplied results are preserved from `revised_solver.zip`. These notes distinguish implementation behaviour from the manuscript wording and from the additional reproduction tools. Validation results are recorded separately. Reproducing the same code is not independent validation against an analytical solution or another implementation.

## 1. Formulations and units

The coordinate is upward and Darcy flux is upward positive. `faces` implements `q = -K(dpsi/dz + 1)`. The mixed residual in `residual` is `dz*(theta_new-theta_old)/dt + diff(q)`. Summing the residuals gives the storage change minus the net boundary inflow. Newton differentiates both storage and conductivity; tests compare its assembled matrix with an independently perturbed residual. The L update uses a constant retention slope bound, lagged conductivity and exact storage at the current iterate. It is a valid stabilised mixed iteration of this discrete system.

Warrick and Polmann use cm and s. Miller and Ireson use m and days. Lehmann uses cm and days. The conductivity values in code convert to the manuscript's cm/s values within their printed rounding. The L values are in inverse length and follow the same benchmark units. `m = 1 - 1/n` is used in every supplied case.

The L-scheme is present for Miller. The four saved Miller L-scheme runs fail to meet the stopping criteria within 10,000 iterations in the first time step. They are not missing results. Such a failure is evidence about this parameter choice, stopping criterion and iteration budget, not a proof that every L-scheme implementation fails on Miller. The hybrid is a distinct algorithm with five L steps before Newton and backtracking.

## 2. RMSE weights and storage

`errors` computes `sqrt(dz * sum(error**2) / H)` over the unknowns stored in each NPZ file. On a cell grid there are `H/dz` unknowns and the weights sum to H. On a vertex grid only the `H/dz - 1` interior unknowns are stored, so their weights sum to `H-dz`. The existing numbers do not use a mean over the count of interior nodes.

The manuscript can retain its RMSE equation and numbers by defining the actual convention. Suggested wording is

> Profile RMSE is calculated over the computed unknowns using a weight of Δz for each term and normalisation by the column length H. For the grids with prescribed pressure head boundaries, the sum includes the interior unknowns. For the cell-centred grids with prescribed surface fluxes, it includes all cells. The reference solution is evaluated at the same locations before the error is calculated.

Delete the blanket statement that the included weights always sum to H. At prescribed head endpoints the boundary errors are zero, but a free-drainage endpoint should not be assigned a fictitious zero error merely to complete a quadrature rule. If a different norm is adopted, recompute the metrics and associated figures instead of relabelling the existing values.

`run` computes storage as `dz * sum(theta)` over the evolved unknowns. Its mass balance uses the matching first and last numerical face fluxes. Thus it is a discrete balance for the evolved control volumes. On vertex grids it does not include endpoint half-volume storage. Make the manuscript's storage sum and boundary flux convention match this calculation. The cell-centred flux benchmarks cover the full column in this sum.

## 3. Capacity at saturation

`Soil.C` is the derivative of the stated retention relation and is zero at and above saturation. `Soil.Cp` instead returns `1e-6` at non-negative pressure head. The value has units of inverse length, so the default means `1e-6 cm^-1` in centimetre cases and `1e-6 m^-1` in metre cases.

The pressure head Picard/Newton residual and the non-iterative implicit scheme use this regularised capacity. Modified Picard uses it in its iteration matrix but retains the exact mixed storage residual. Mixed Newton uses `C`, and the L-scheme uses L. For a converged mixed solution the Picard matrix regularisation does not add storage to the residual. For pressure head formulations it does change the saturated storage term.

This convention must be disclosed beside the capacity definition and pressure head formulation. Do not state that every implemented storage residual uses exactly `C = dtheta/dpsi` at saturation or that no storage regularisation is present. Suggested wording is

> The pressure head formulations use the derivative of the retention curve for ψ < 0 and a small capacity of 10⁻⁶ per unit length for ψ ≥ 0, following the implementation used in the original benchmarks. Modified Picard uses the same value in its iteration matrix at saturation, while its residual retains the exact change in water content. The mixed Newton and L-scheme residuals also retain this exact storage change.

The units should be stated explicitly for the centimetre and metre benchmarks. The value is not a measured soil-specific storage coefficient. Its effect is particularly relevant to saturated Miller solutions; no sensitivity study is supplied. Altering it would change a benchmark configuration and requires a checked rerun.

## 4. Backtracking behaviour

In `step`, backtracking checks an Armijo-like residual decrease with coefficient `1e-4` and halves the update. When the factor reaches `1/256`, the current implementation accepts that update without rechecking the decrease condition. The separate residual and increment tests must still pass before the time step is accepted.

Accordingly, describe this as bounded backtracking, not a guaranteed residual decrease at every Newton update. Suggested wording is

> In the hybrid method, Newton updates are reduced by repeated halving when the residual decrease test is not met. The reduction factor is bounded below by 1/256. At this bound, the update is attempted even if sufficient decrease has not been established. A time step is accepted only after the residual and increment tolerances are both satisfied.

If the intended algorithm requires sufficient decrease for every accepted update, the implementation should instead reject an unsuccessful line search. That is a numerical change and needs new results; it has not been silently introduced into this archive.

## 5. Completion, admissibility and failure counters

`completed` records termination at the scheduled final time. It is not a stability or admissibility certificate. The explicit inverse retention function returns zero pressure head when water content exceeds saturation without reducing the stored water content. The supplied Warrick runs at 900 s and 1800 s reach maximum water contents of approximately 0.49766 and 0.50516, above theta_s = 0.495. They should remain identified as oscillatory/inadmissible comparison results, not successful stable solutions. Inspect water content as well as pressure head, because the inverse mapping masks oversaturation in pressure head.

When a run fails before its first accepted step, the original reporting code inserts a dummy zero iteration entry. It therefore records `n_steps = 1`, although `t_end = 0` and zero steps were accepted. `it_total` counts iterations of accepted steps, not all work spent on the failed step. This does not change the completed-run means in the manuscript, but failure counters must not be interpreted as total attempted computational work. Use the failure status and reason, or derive zero accepted steps when `t_end = 0`. A future reporting fix should distinguish attempted and accepted work explicitly.

## 6. Forcing dates and supplementary stability check

Lehmann integrates 59 daily intervals. Its array contains an initial zero followed by 59 forcing values. The latest available revised manuscript already states 59 values. Ireson has 3653 dated records, including the initial state, and integrates 3652 one-day intervals; forcing starts at index 1. This preserves the notebook convention. Distinguish record count from elapsed days when describing the final time.

The ordinary Polmann run list includes 42, 60, 90 and 126 s but not 50 s. The 50 s diagnostic is placed after `raise SystemExit` in `make_figures.py` and is unreachable. An independent execution during this assessment confirmed failure at 50 s after two accepted steps. The supplemental script saves that evidence. This is an observed failure at the tested settings, not proof that every time step above 50 s fails.

## 7. Reproduction, provenance and plots

All 109 supplied CSV rows match their summary JSON values. Recomputing the saved profile errors from the NPZ files gives the same summary errors. The author supplied the manuscript's computing environment on 20 November 2026. It is recorded in `manuscript_environment.json` and the README. The reproduction tool records its own environment and keeps original outputs intact; the validation measurements in `validation/environment.json` are separate from the manuscript timings.

The complete checkout is required for `notebooks/ireson/infiltration.dat` and `T_Level.out`. Figure 1 is supplied as an image without a generation script. Figures 2–15 can be regenerated. Figure 9 depends on runtime; Figure 15 depends on iteration counts. If either quantities or profiles change, inspect every affected figure and manuscript number rather than assuming only runtime changed.

The current script uses permissive JSON NaN values for undefined metrics. Python reads these files, but strictly conforming JSON consumers may need NaN converted to null. Undefined ratios should remain undefined rather than being replaced with zero.
