# Agent Action Gate — examples

Valqore's flagship differentiator: **governing the AI agents that now govern your infra.**
Two complementary capabilities live here.

## 1. `agent-audit` — score an agent fleet's posture

The *same* agent workload, done two ways:

| File | Verdict | Why |
|------|---------|-----|
| [`ungoverned-agent.yaml`](ungoverned-agent.yaml) | **UNGOVERNED** (45.9) | Shared/default service account, privileged + root, no kill-switch, no rate limit, no blast-radius cap, no audit sink |
| [`governed-agent.yaml`](governed-agent.yaml) | **GOVERNED** (94.6) | Dedicated identity, OIDC + signed delegation, step/token/timeout caps, telemetry, escalation, default-deny egress, non-root, pinned by digest |

```bash
valqore agent-audit ungoverned-agent.yaml   # -> UNGOVERNED
valqore agent-audit governed-agent.yaml      # -> GOVERNED
valqore agent-audit ./                        # -> PARTIAL (1 of 2 governed)
```

`agent-audit` scores five dimensions — Identity & Access, Guardrails & Limits, Boundary &
Delegation, Oversight & Audit, Model Supply Chain — and rolls them up to a
GOVERNED / PARTIAL / UNGOVERNED fleet verdict. Add `--format oscal -o agentgov.json` for an
auditor-ready evidence pack.

## 2. `agent-gate run` — stop a risky action before it lands

[`terraform-plan.json`](terraform-plan.json) is a plan an agent (or SRE bot) proposes: it
deletes a prod database and creates a `0.0.0.0/0` security group → **blast radius HIGH**.

```bash
valqore agent-gate run --tf-plan terraform-plan.json --agent sre-bot --max-blast-radius medium
```

The action is **BLOCKED** (exit code 2) because its blast radius exceeds the `medium` cap.
Add `--request-approval` to mint a signed approval request, recorded in the agent-gate journal
as audit evidence (EU AI Act / NIST / SoD).

> The `valqore` alias is set up in the [repo README Quickstart](../../README.md#quickstart-60-seconds).
