# Complete the archive

## Before release

1. Read `final_solver/VALIDATION_REPORT.md`. Align the final manuscript with the actual storage, RMSE, saturation and line-search conventions.
2. The revised code is licensed under MIT, as selected by the author on 20 November 2026. The root `LICENSE`, README and `CITATION.cff` now record this choice. Preserve the stated scope, third-party attribution and separately applicable terms; the earlier Zenodo v1.0.1 record remains unchanged.
3. Confirm the authors in `CITATION.cff`. Add only verified ORCIDs. Vassilis Glenis also has a Willis Research Network affiliation in the latest available manuscript; confirm its representation in the archive.
4. The manuscript's reported computing environment is recorded in `final_solver/manuscript_environment.json` and its README. Retain the supplied runtimes with that description. A fresh timing exercise is optional and can use `python reproduce.py --output reproductions/laptop`. Inspect `comparison.json` and `environment.json` before adopting any new measurements. References are copied unless `--recompute-references` is selected.
5. If new results, tables or figures are adopted, use a separate checked commit with the measured environment and update every affected manuscript value. Check the final manuscript PDF and response-letter line references before submission.
6. Merge preparation changes only after these decisions and checks. Do not publish v2.0.0 from an unfinished preparation branch.

## Connect and archive

1. Sign in to Zenodo, open its GitHub page, sync repositories if needed and enable `juanpablodelafuente/richards-benchmark`.
2. Confirm association with the existing series. Current version DOI `10.5281/zenodo.16806592` identifies `v1.0.1`. Concept DOI `10.5281/zenodo.16806591` identifies the series. These were checked using public Zenodo and DataCite metadata on 19 November 2026.
3. After the integration and metadata are correct, publish a GitHub release tagged `v2.0.0` from the final checked commit. Use `RELEASE_NOTES.md`. GitHub Desktop is optional.
4. Wait for processing and inspect Zenodo's GitHub status and any errors. Five minutes is not guaranteed. Inspect the resulting record; do not assume it is an unpublished draft.
5. Check creators, ORCIDs, affiliations, licence, version and links. Metadata can be edited after publication. The old record currently names only `JP_delaf`; its creator metadata can be corrected separately.
6. Copy the new version DOI. If GitHub integration is unavailable, create a new version from the existing record and upload a clean source ZIP from the final commit. Exclude `.git`, virtual environments, caches and temporary reproductions. Avoid a separate unrelated series or using both archival routes for the same version.
7. Add the new DOI to the manuscript and repository citation information. A metadata-only commit after archiving is normal; do not silently change the files identified by the cited release.
8. Add the work to ORCID through DataCite or its DOI. Each co-author controls their ORCID authorisation. Correct creator ORCIDs also support DataCite auto-update when enabled by each author.

## Manuscript wording after publication

The Python code, reference solutions and numerical results are available in Zenodo as version 2.0.0 at [new version DOI], archived from https://github.com/juanpablodelafuente/richards-benchmark. The original notebooks are preserved in version 1.0.1 at https://doi.org/10.5281/zenodo.16806592.

Replace the bracketed DOI after assignment. The revised Word manuscript supplied on 20 November 2026 provided the computing details. Final response-letter line references need checking against the final manuscript layout.

## Official guidance

- https://help.zenodo.org/docs/github/enable-repository/
- https://help.zenodo.org/docs/github/archive-software/github-upload/
- https://help.zenodo.org/docs/github/describe-software/citation-file/
- https://help.zenodo.org/docs/deposit/manage-versions/
- https://help.zenodo.org/docs/deposit/manage-records/
- https://support.datacite.org/docs/datacite-and-orcid
