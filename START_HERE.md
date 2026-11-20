# Using this prepared repository

This package combines the original GitHub repository with the supplied revised solver and additional reproduction tools. It prepares version 2.0.0. It does not mean that a new release or Zenodo DOI has been published.

## What to do

1. Read `revised_solver/VALIDATION_REPORT.md` for the actual checks and `revised_solver/ARCHIVE_NOTES.md` for the few implementation details to reconcile with the final manuscript.
2. The revised code now uses MIT, as authorised by the author on 20 November 2026. The final text is in `LICENSE`, and the root README states its scope.
3. The manuscript's reported computing environment is recorded in `revised_solver/manuscript_environment.json`. The supplied runtimes are retained. A new timing exercise is optional; the separate reproduction command records its own environment without deleting the archive.
4. The prepared files are already uploaded to the `prepare-v2-archive` branch in pull request #1 at https://github.com/juanpablodelafuente/richards-benchmark/pull/1. Review and merge the preparation when the manuscript and archive are ready.
5. Use `release/RELEASE_CHECKLIST.md` to connect Zenodo and publish the final checked version.

## Safe laptop command

After installing the requirements in an isolated Python environment, open a prompt in `revised_solver` and run

```text
python reproduce.py --output reproductions/laptop
```

The output directory must be new. The command records the actual environment, reruns the ordinary configurations, copies the reference solutions, writes the combined CSV and regenerates Figures 2–15. Inspect `comparison.json` before transferring any results into the manuscript. The separate validation report documents independent reference reruns performed during preparation.

## Preserved files

The numerical kernel, original run configuration, figure script, notebook comparison script, requirements and all supplied results, table and figures are unchanged. Checksums are in `revised_solver/archived_checksums.sha256`. The two README files have been updated. Original notebooks and input data are unchanged. The computing details were read from the revised manuscript supplied on 20 November 2026. Final response-letter line references still need checking against the final manuscript layout.
