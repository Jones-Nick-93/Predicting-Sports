# Validation Approach

The main SQL file is a publication-safe template, not a configured query bundle.
Placeholders intentionally prevent it from running unchanged against an unknown system.

Automated CI validates the properties that must remain true in public:

- original system names and field fingerprints remain absent;
- fictional placeholders remain present;
- no data-changing, permission-changing, backup, or restore statements are introduced;
- dynamic identifiers continue to use `QUOTENAME`;
- searched values remain parameters to `sp_executesql`.

Functional execution belongs in a disposable SQL Server database populated with
fabricated tables and values. It should never require production access or a copied
vendor schema. Because dynamic discovery cost depends on table width and row count,
performance evidence from a toy fixture would not establish production safety.
