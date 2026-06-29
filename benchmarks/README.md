# Valqore benchmark — reproducible

A **head-to-head** you can re-run yourself: Valqore vs other scanners on one
shared corpus. No private artifacts — Valqore runs from the public, signed image.

```bash
# 1. Valqore runs via the public image — no install, no source
docker pull ghcr.io/valqore/engine:latest

# 2. Add any competitor you want included (isolated install)
pipx install checkov          # the de-facto OSS IaC baseline (the engine behind Prisma Cloud)

# 3. Run from the repo root
python benchmarks/run_benchmark.py
```

This writes `RESULTS.md` (committed here as a reference run) and `results.json`.

> **Why pipx for Checkov?** Checkov pins an old `python-hcl2`; install it isolated
> (pipx or a separate venv), not into a shared environment. The harness only runs
> the standalone `checkov` on PATH. Kubescape / Trivy / kube-score are auto-included
> when present on PATH too — absent tools are skipped and clearly marked.
>
> The harness invokes Valqore as `valqore` if it's on your PATH (e.g. the Docker
> alias from the [repo README](../README.md#quickstart-60-seconds)), otherwise it
> runs `ghcr.io/valqore/engine:latest` via Docker automatically.

## What's in the corpus

`corpus/` is a deliberately realistic, messy repo — Kubernetes manifests, a
Terraform file, and a Dockerfile — containing:

- **Bread-and-butter security misconfigs** every scanner should catch (privileged
  container, `:latest`, no securityContext, open `0.0.0.0/0` SSH, public/unencrypted
  S3, root Dockerfile). Deliberate — rivals get **fair credit**.
- **Cost waste** — an over-provisioned 10× batch worker, a 4×GPU inference deploy
  with no limits — invisible to security scanners.
- **Ungoverned AI** — an LLM/agent workload with no auth, no risk classification,
  no rate limit, a hardcoded API key, no AgentCard.
- **Compliance + carbon** gaps that only surface when those domains are evaluated.

Every corpus file is SHA-256 hashed in the provenance block of `RESULTS.md`, so a
reviewer can confirm they ran the exact same inputs.

## The honest point

Raw finding **counts** across tools are not directly comparable — different rules,
different granularity. The benchmark is about **domain coverage** (what each tool
can see *at all*) and the converged single-verdict + machine-readable evidence
story. A security/IaC scanner structurally cannot report cost, carbon, AI
governance, or compliance findings; Valqore reports all of them in one pass. See
[METHODOLOGY.md](METHODOLOGY.md) for corpus design, normalization, and caveats.

Numbers will vary with engine and tool versions — that's the point of letting you
re-run it.
