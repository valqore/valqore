# Valqore benchmark — converged governance vs point scanners

Corpus: `benchmarks/corpus/` (Kubernetes + Terraform + Dockerfile — insecure,
over-provisioned, and ungoverned-AI by design).

> Honest note: raw finding *counts* across tools are not directly comparable
> (different rule granularity). The point is **domain coverage** — what each tool
> can see at all — and the converged single-verdict + evidence story. See
> [METHODOLOGY.md](METHODOLOGY.md) for corpus design, normalization, and caveats.

## Provenance

- Reference run: 2026-06-29 (engine `ghcr.io/valqore/engine:1.7.0`)
- Corpus: 5 files, sha256 `b44436bee8752a30` (the harness recomputes this on every run)
- Tools this run: Valqore (public image), Checkov `pipx`. Kubescape / Trivy /
  kube-score not installed — sourced from the capability matrix below.

## Same corpus, what each tool reports

**Valqore** — 1,694 evaluations, **232 findings across 10 domains**; Score
**10/100** (Grade F), verdict **BLOCK**. One pass, one score, OSCAL evidence.

| Domain | Valqore findings |
|---|---:|
| AI governance | 72 |
| Cost / FinOps | 56 |
| Compliance | 50 |
| Security | 18 |
| Dockerfile | 16 |
| Carbon / GreenOps | 6 |
| GPU / AI cost | 4 |
| IaC (Terraform) | 4 |
| Supply chain | 3 |
| Reliability / Ops | 3 |

**Checkov** — **62 failed checks** (terraform: 14, kubernetes: 45, dockerfile: 3);
security / IaC misconfig only — no cost, carbon, AI governance, compliance
evidence, or single verdict.

_Kubescape / Trivy / kube-score: not installed in this run — see the capability
matrix (sourced from the 2026 review)._

Valqore catches the same security/IaC misconfigs Checkov does, **and** the cost,
carbon, AI-governance, and compliance findings Checkov structurally cannot — in
one pass, with one score and machine-readable OSCAL evidence.

## Capability matrix

| Capability | Valqore | Checkov | Kubescape | kubeadapt | Wiz |
|---|:---:|:---:|:---:|:---:|:---:|
| K8s security misconfig | ✅ | ✅ | ✅ | ◑ | ✅ |
| IaC (Terraform) scanning | ✅ | ✅ | ◑ | — | ✅ |
| Dockerfile scanning | ✅ | ✅ | ✅ | — | ◑ |
| Cost / FinOps | ✅ | — | — | ✅ | — |
| Carbon / GreenOps | ✅ | — | — | ✅ | — |
| AI / LLM governance | ✅ | — | — | — | ◑ |
| Agent / MCP runtime gate | ✅ | — | — | — | ◑ |
| Single 0–100 score + verdict | ✅ | — | — | — | — |
| Machine-readable OSCAL evidence | ✅ | — | — | — | ◑ |
| Auto-remediation | ✅ | ◑ | — | ◑ | — |
| Self-hosted / air-gapped | ✅ | ✅ | ✅ | ◑ | — |

✅ full · ◑ partial · — not offered. Competitor rows are sourced from public
docs/the 2026 review; re-run with each tool installed to populate live numbers.

## Reproduce

```bash
docker pull ghcr.io/valqore/engine:latest
pipx install checkov
python benchmarks/run_benchmark.py    # from the repo root
```

Numbers vary with engine and tool versions — that's why this is yours to re-run.
