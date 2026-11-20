# Using this prepared repository

This package combines the original GitHub repository with the supplied revised solver and additional reproduction tools. It prepares version 2.0.0. It does not mean that a new release or Zenodo DOI has been published.

## What to do

1. Read `revised_solver/VALIDATION_REPORT.md` for the actual checks and `revised_solver/ARCHIVE_NOTES.md` for the few implementation details to reconcile with the final manuscript.
2. Settle the licence. GitHub's old README says MIT, while Zenodo v1.0.1 lists CC BY 4.0. A proposed MIT file is in `release/`. Do not publish it as an adopted licence until the authors confirm the choice and scope.
3. Decide which computing environment the paper will report. If the original environment cannot be documented, use the safe reproduction command on your laptop. No original results need to be deleted.
4. If remote upload was unavailable, clone your repository with GitHub Desktop. Copy the contents of this prepared folder into the cloned repository root. `revised_solver` must sit beside `notebooks`, not inside it. Do not replace the clone's `.git` folder. The supplied archive does not contain a `.git` folder.
5. In GitHub Desktop, inspect the changed files, commit the preparation and push. Review the manuscript clarifications before creating a release.
6. Use `release/RELEASE_CHECKLIST.md` to connect Zenodo and publish the final checked version.

## Safe laptop command

After installing the requirements in an isolated Python environment, open a prompt in `revised_solver` and run

```text
python reproduce.py --output reproductions/laptop
```

The output directory must be new. The command records the actual environment, reruns the ordinary configurations, copies the reference solutions, writes the combined CSV and regenerates Figures 2–15. Inspect `comparison.json` before transferring any results into the manuscript. The separate validation report documents independent reference reruns performed during preparation.

## Preserved files

The numerical kernel, original run configuration, figure script, notebook comparison script, requirements and all supplied results, table and figures are unchanged. Checksums are in `revised_solver/archived_checksums.sha256`. The two README files have been updated. Original notebooks and input data are unchanged. No new manuscript PDF was available in this preparation task.
