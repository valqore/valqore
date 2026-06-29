# Govern kagent agents with Valqore

[kagent](https://kagent.dev) (CNCF Sandbox / Solo.io) is a fast-growing agentic
framework: you `kubectl apply` an `Agent` CRD and it runs in your cluster,
delegates work to other agents (A2A), and calls tools over MCP. It's great at
*running* agents -- and it enforces no deterministic policy, caps nothing, and
emits no compliance evidence.

**Valqore is the independent governance + enforcement layer over it.** Same
deterministic engine, same rules as your CI/CD gate, admission webhook, and OSCAL
export -- now pointed at your kagent fleet. No SaaS, no agent SDK lock-in, no
opt-in labels required.

This is a runnable, end-to-end proof against the manifests in this directory.

```bash
python examples/kagent_governance/demo.py
```

It drives the **real `valqore` CLI** (no mocks) through five steps.

---

## What it shows

### 1+2. Audit an *ungoverned* kagent fleet, grounded in telemetry

`valqore agent-audit agents-ungoverned.yaml --telemetry telemetry.prom`

The manifests carry **no Valqore labels or annotations**. Valqore still:

- **Discovers every agent** -- it natively understands the `kagent.dev` `Agent`
  CRD (no `kind: Deployment` required). *(P-1)*
- **Maps the delegation graph** and flags the `troubleshooter → remediation →
  troubleshooter` **cycle** as CRITICAL, plus unverifiable (unsigned) delegation.
  *(P-4)*
- **Fingerprints a shadow agent**: `byo-research-agent` is a plain LangGraph
  `Deployment` with no governance label -- Valqore identifies the runtime and
  flags it as a **shadow agent** no GRC tool would ever see. *(P-6)*
- **Grounds guardrails in observed behaviour**: the troubleshooter ran **1,500
  steps / 240 tool calls / 1.85M tokens** last window with **no declared cap** ->
  HIGH `unbounded_observed`. Annotations claim nothing; telemetry proves it ran
  hot. *(P-5)*

Verdict: **UNGOVERNED**.

### 3. The *same* agent, brought to GOVERNED -- on evidence, not annotations

`valqore agent-audit agents-governed.yaml`

`agents-governed.yaml` adds the governance annotations **and** the real resources
that back them: a dedicated, token-isolated `ServiceAccount`
(`automountServiceAccountToken: false`) and a **default-deny egress
NetworkPolicy** that selects the agent. Valqore verifies these **cross-resource**
-- it won't take `egress-policy: default-deny` on faith without a policy object
that enforces it. *(P-7)*

Verdict: **GOVERNED**. (Service-mesh shops: an Istio `Sidecar` or Cilium policy
satisfies the egress evidence too.)

### 4. Gate kagent's live MCP tool calls -- deterministically, per agent

`valqore mcp-gate check <tool> --agent <name> --policy mcp-policy.json`

kagent agents act through MCP. `mcp-policy.json` scopes each agent to least
authority:

| Call | Agent | Decision |
|------|-------|----------|
| `k8s_delete_resource` | `k8s-troubleshooter` (read-only scope) | **BLOCK** |
| `k8s_get_pods` | `k8s-troubleshooter` | **ALLOW** |
| `helm_uninstall` | any | **BLOCK** (destructive verb -> high blast radius) |

The same policy runs inline in front of a live MCP server with
`valqore mcp-gate serve <upstream> -p mcp-policy.json`, writing an HMAC-signed
evidence journal of every decision. *(P-3)*

### 5. Push enforcement into the API server -- gate the CRD at admission

`valqore vap-export -r AIG-145,AIG-150 --agent-crds`

Compiles the agent rules to a native Kubernetes **ValidatingAdmissionPolicy**
whose `matchConstraints` target `kagent.dev/agents` directly. The cluster rejects
a non-compliant `Agent` at `kubectl apply` time, with **Valqore out of the data
path**. *(P-2)*

---

## Files

| File | Purpose |
|------|---------|
| `agents-ungoverned.yaml` | Raw kagent fleet: CRD agents, a delegation cycle, a shadow BYO agent |
| `agents-governed.yaml` | The same agent + dedicated SA + default-deny egress NetworkPolicy |
| `telemetry.prom` | Observed runtime counters (Prometheus / OTel gen_ai shape) |
| `mcp-policy.json` | Per-agent MCP tool scopes + destructive-verb deny |
| `demo.py` | Driver that runs the real CLI through all five steps |

Everything here is throwaway sample data -- the demo writes nothing outside its
own process and leaves no state behind.

## For auditors

Add `--format oscal -o evidence.json` to any `agent-audit` run for a NIST OSCAL
assessment record (delegation, runtime, and egress findings fold into the mapped
controls), ready for an EU AI Act / NIST AI RMF / SOC 2 evidence package.

A real sample is committed here as
[`sample-evidence.oscal.json`](sample-evidence.oscal.json) -- the OSCAL output of
the ungoverned audit above, with findings across all five control dimensions.
Regenerate it with:

```bash
valqore agent-audit agents-ungoverned.yaml --telemetry telemetry.prom \
  --format oscal -o sample-evidence.oscal.json
```
