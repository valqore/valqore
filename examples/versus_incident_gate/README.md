# Gate a runbook-reading incident agent with Valqore

[Versus Incident](https://github.com/versuscontrol/versus-incident)'s
`find_runbook` tool uses RAG (embeddings + cosine retrieval) to surface the
*right* runbook during an incident -- semantic search instead of keyword search,
so an alert that says "too many clients already" finds the runbook titled
"connection pool exhausted." It is deliberately read-only: "no writes, no
remediation, no paging. The agent reads the result; a human still decides."

That posture is exactly right. It is also **one wire away from danger**: the
runbook it retrieves ([`runbook.md`](runbook.md)) ends with *"roll back the api
deploy."* The instant an agent can act on what it reads, the recommendation
becomes an action -- and that action needs a deterministic gate.

**Valqore is that gate.** Versus Incident finds the runbook; Valqore decides
whether the agent may execute what the runbook recommends.

```bash
python examples/versus_incident_gate/demo.py
```

## What it shows

The policy ([`mcp-policy.json`](mcp-policy.json)) scopes two agents and routes
destructive verbs through signed approval.

### A. Read-only `incident-responder` (the Versus Incident posture)

| Tool call | Maps to | Decision |
|-----------|---------|----------|
| `find_runbook` | retrieve the runbook | **ALLOW** (in scope, read-only) |
| `pg_query` | runbook step 1 -- `SELECT count(*)` | **ALLOW** |
| `pg_terminate_backend` | runbook step 2 -- terminate idle txns (a write) | **BLOCK** (out of scope) |
| `argo_rollback` | runbook step 3 -- "roll back the api deploy" | **BLOCK** (out of scope) |

The responder can read everything and execute nothing destructive -- even when a
retrieved runbook tells it to.

### B. Privileged `remediation-agent` -- a human still decides

| Tool call | Decision |
|-----------|----------|
| `argo_rollback` | **BLOCK** -- high blast radius, held for a signed approval |
| `argo_rollback --approved` | **ALLOW** -- "high blast radius approved" |

This is the article's "a human still decides," now *enforced*: the destructive
step is held until an HMAC-signed approval exists, and every decision lands in the
tamper-evident journal (`valqore mcp-gate journal`).

## Ground the fix in your own runbooks (offline)

Valqore can also do the *retrieval* half deterministically -- no embeddings, no
external model call, no data egress (the article ships incident text to an
external embedding endpoint; Valqore doesn't have to). `valqore runbook` grounds a
finding in your Markdown or Confluence runbooks and flags the destructive steps:

```bash
valqore runbook "too many clients postgres connection pool exhausted on api" \
  --source examples/versus_incident_gate
```

```
1. Postgres connection pool exhausted   (tags: postgres; body overlap 8/8)
   - Check active connections (read-only)
   ! Terminate idle-in-transaction sessions   (destructive: 'terminate' -- route through the gate)
   ! Roll back the api deploy                  (destructive: 'rollback' -- route through the gate)
```

Confluence works the same way via `--confluence space-export.json` (the live
Cloud REST `body.storage` shape). The retrieval surfaces the documented fix; the
gate (above) decides whether the agent may execute the destructive steps it found.

## The data-boundary angle (backlog)

Versus Incident also does the right thing on egress: it **redacts secrets/PII
before embedding** ("redaction first, embedding second -- not the other way
around"), because the embedding call crosses an external model boundary. Valqore
covers this with **AIG-176** (redaction/DLP before external model egress): an
agent calling an external LLM/embedding endpoint must declare a redaction step,
run a DLP sidecar, or pin an on-prem model -- the data-layer complement to the
network-egress check (NetworkPolicy / Istio / Cilium).

## Files

| File | Purpose |
|------|---------|
| `runbook.md` | The retrieved runbook (the article's Postgres pool-exhaustion case) |
| `mcp-policy.json` | Per-agent tool scopes + destructive-verb approval routing |
| `demo.py` | Driver that runs the real `valqore mcp-gate` through both scenarios |

Throwaway sample data; the demo writes nothing outside its own process.
