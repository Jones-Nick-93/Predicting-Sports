# Public Repository Rules

- Use only fabricated DataFrames, workbook names, paths, schemas, and dates.
- Never add source queries, real workbook contents, company identifiers, network paths,
  credentials, production schedules, or report-specific business rules.
- Preserve explicit reconciliation modes; do not infer data grain or duplicate semantics.
- Keep writes recoverable through same-directory temporary files and optional backups.
- Add deterministic temporary-workbook tests for every behavior change.
- Before publication, scan both files and Git history and preserve the MIT license notice.
