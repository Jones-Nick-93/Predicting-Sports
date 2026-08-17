# Public Repository Rules

- Keep this project provider-neutral and use only reserved domains and fabricated payloads.
- Never add real endpoints, credential fields, tenant IDs, account IDs, vendor responses,
  production retry settings, or operational resource identifiers.
- Keep destructive examples in dry-run mode and preserve the explicit confirmation gate.
- Add deterministic fake-transport tests for every behavior change.
- Before publication, scan both files and Git history for secrets and infrastructure data.
