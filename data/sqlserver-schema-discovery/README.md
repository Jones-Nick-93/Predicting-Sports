# SQL Server Schema Discovery

A read-only SQL toolkit for investigating unfamiliar or poorly documented relational
schemas through measurement rather than assumptions.

The project is deliberately vendor-neutral. Names such as `YOUR_SCHEMA`, `YOUR_TABLE`,
`YOUR_KEY_COLUMN`, and `STATUS_FLAG_A` are fictional placeholders and must be replaced
by an authorized user before execution.

## Included investigations

| Block | Purpose |
| --- | --- |
| 1 | Inventory columns and declared types |
| 2 | Inspect a bounded sample for a known key |
| 3 | Find which text column holds a known value within one table |
| 4 | Find a known value across a filtered schema |
| 5 | Search table names by fragment |
| 6 | Profile text-column fill rate and cardinality |
| 7 | Profile interactions among caller-selected status flags |
| 8 | Detect caller-supplied sentinel dates |
| 9 | Generate candidate join evidence from sampled key overlap |

## Method

1. Confirm that expected objects exist.
2. Inspect a bounded record that is already understood from an authorized source.
3. Profile population and cardinality before treating a field as meaningful.
4. Detect sentinel values before temporal analysis.
5. Profile related flags jointly rather than assuming they are independent.
6. Treat value overlap as candidate join evidence, then verify grain and cardinality.

## Safety

- Every executable statement is `SELECT` or metadata inspection through
  `INFORMATION_SCHEMA`.
- Dynamic identifiers are wrapped with `QUOTENAME`; searched values are passed to
  `sp_executesql` as parameters.
- Use a read-only login with access limited to the intended database and schema.
- Run broad profiling against a reporting replica or bounded development database.
- Blocks 4 and 6 can be expensive on large or wide schemas. Narrow the filters first.
- Query results may contain sensitive data even though this repository does not.
  Do not commit exported results, screenshots, query plans, or logs.

## Requirements

- Microsoft SQL Server
- Read access to the intended database
- Permission to query `INFORMATION_SCHEMA`

## Validate the public template

```bash
python -m unittest -v tests/test_public_safety.py
```

This validates the read-only and publication contracts without connecting to a real
database. See `docs/validation.md` for why the placeholders are intentional.

## Publication boundary

This copy contains no real database, server, schema, table, column, key, customer,
vendor, account, or production-derived field interpretation. It includes no query
results and makes no claims about a specific ERP installation.

Released under the MIT License. See `LICENSE`.
