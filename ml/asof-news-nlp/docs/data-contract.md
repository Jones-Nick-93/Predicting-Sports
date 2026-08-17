# Data contract

One event has a binary synthetic label and three document revisions: early ambiguous,
later definitive, and post-event recap. Each revision has document/event identity,
revision number, text, publication, ingestion, and feature-availability timestamps.
Labels become usable only after settlement. Missing, deleted, conflicting, or late
real-world documents are unsupported and would require explicit states.
