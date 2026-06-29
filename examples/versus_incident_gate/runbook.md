---
title: Postgres connection pool exhausted
service: api
tags: [postgres, connection-pool, database]
---

# Postgres connection pool exhausted

**Symptoms:** `FATAL: remaining connection slots are reserved`, "too many clients
already", api error rate climbing.

## Remediation

1. Check active connections (read-only):
   `SELECT count(*) FROM pg_stat_activity;`
2. Terminate idle-in-transaction sessions:
   `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction';`
3. Roll back the api deploy that raised the pool ceiling.

> Steps 2 and 3 change production. A retrieval tool may *surface* this runbook,
> but executing these is a write -- it must pass the gate.
