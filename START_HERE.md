# Using this prepared repository

This package combines the original GitHub repository with the supplied revised solver and additional reproduction tools. It prepares version 2.0.0. It does not mean that a new release or Zenodo DOI has been published.

## What to do

1. The revised code now uses MIT, as authorised by the author on 20 November 2026. The final text is in `LICENSE`, and the root README states its scope.
2. The manuscript's reported computing environment is recorded in `final_solver/manuscript_environment.json`. The supplied runtimes are retained. A new timing exercise is optional; the separate reproduction command records its own environment without deleting the archive.
3. The prepared files are on the `Richards_solvers_assessment` branch. The earlier pull request #1 was closed without merging after the branch was renamed. Create a pull request from `Richards_solvers_assessment` into `main`, then review and merge it when the manuscript and archive are ready.
4. Use `release/RELEASE_CHECKLIST.md` to connect Zenodo and publish the final checked version.

## Safe laptop command

After installing the requirements in an isolated Python environment, open a prompt in `final_solver` and run

```text
python reproduce.py --output reproductions/laptop
```

The output directory must be new. The command records the actual environment, reruns the ordinary configurations, copies the reference solutions, writes the combined CSV and regenerates Figures 2–15. Inspect `comparison.json` before transferring any results into the manuscript.

## Preserved files

The numerical kernel, original run configuration, figure script, notebook comparison script, requirements and all supplied results, table and figures are unchanged. Checksums are in `final_solver/archived_checksums.sha256`. The two README files have been updated. Original notebooks and input data are unchanged. The computing details were read from the revised manuscript supplied on 20 November 2026. Final response-letter line references still need checking against the final manuscript layout.
