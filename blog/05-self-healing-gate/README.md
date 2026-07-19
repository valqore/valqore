# Blog Post #5 — Who Approves the Machine?

Example files for the blog post **"Move 8: Who Approves the Machine?"** — putting
a deterministic gate in front of an AI self-healer (K8sGPT, Robusta, an Azure/AWS
SRE agent, your own scripts) so autonomous remediation is authorized, bounded,
and signed.

Try it on the **free, tokenless public image** — no key, no signup:

```bash
docker pull ghcr.io/valqore/engine:1.12.1
```

## Try It

### 1. The healer's convenient "quick fix" — a privileged host-debug pod — is BLOCKED

```bash
docker run --rm -v "$(pwd):/workspace" ghcr.io/valqore/engine:1.12.1 \
  valqore agent-gate run /workspace/remediation-privileged.yaml \
  --language kubernetes --agent sre-bot
```

Expected: **BLOCK** — `SP-007` (CRITICAL): privileged + hostNetwork + hostPID + node-root mount.

### 2. The same fix at L1 (advisory) — see the verdict, block nothing

```bash
docker run --rm -v "$(pwd):/workspace" ghcr.io/valqore/engine:1.12.1 \
  valqore agent-gate run /workspace/remediation-privileged.yaml \
  --language kubernetes --agent sre-bot --autonomy L1
```

Expected: the same verdict is reported, but exit 0 — advisory mode evaluates
everything and blocks nothing. This is the silent rollout: turn the gate on, see
what it *would* do, break nothing.

### 3. A sensible hardening fix — limits, probes, hardened securityContext — is ALLOWED

```bash
docker run --rm -v "$(pwd):/workspace" ghcr.io/valqore/engine:1.12.1 \
  valqore agent-gate run /workspace/remediation-hardened.yaml \
  --language kubernetes --agent sre-bot --max-severity CRITICAL
```

Expected: **ALLOW** — a genuine posture improvement, low blast radius, nothing
CRITICAL. Under a supervised auto-remediation posture it would auto-apply.

### 4. The autonomy ladder — one flag, four levels

```bash
# advisory -> gated -> supervised (+ signed approvals + budgets) -> autonomous (+ earned trust, twin preflight, kill-switch)
for L in L1 L2 L3 L4; do
  docker run --rm -v "$(pwd):/workspace" ghcr.io/valqore/engine:1.12.1 \
    valqore agent-gate run /workspace/remediation-hardened.yaml \
    --language kubernetes --agent sre-bot --autonomy $L --max-severity CRITICAL
done
```

### 5. The 3am command + the evidence

```bash
# fleet-wide kill-switch: degrades every L4 agent to supervised; only ever removes autonomy
docker run --rm ghcr.io/valqore/engine:1.12.1 valqore agent-gate kill-switch status

# the signed, tamper-evident decision journal (proposal -> verdict -> approver -> outcome)
docker run --rm ghcr.io/valqore/engine:1.12.1 valqore agent-gate verify-chain
```

## Files

- `remediation-privileged.yaml` — the healer's convenient "quick fix": a privileged, hostNetwork/hostPID pod mounting node root (BLOCKED, `SP-007`).
- `remediation-hardened.yaml` — a sensible fix: resource limits + probes + a hardened `securityContext` (ALLOWED, low blast).

## What the gate does

| Move | Mechanism |
|------|-----------|
| Deterministic verdict | Rules decide, same input → same verdict; failing rule IDs returned |
| Identity required (L2+) | An anonymous agent is ungovernable — refused before evaluation |
| Cumulative budgets (L3+) | Rolling-window caps on cost/actions/high-blast — the overnight-loop guard |
| Earned auto-approval (L4) | A pattern auto-approves only after N clean **signed** human approvals; high-blast never |
| Kill-switch | One command degrades the whole fleet to supervised — only ever removes autonomy |
| Portable evidence | Every decision chain-signed; export OSCAL / OpenTelemetry for auditors + your SIEM |
