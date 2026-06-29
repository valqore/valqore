# Benchmark methodology

This document is the honest companion to `RESULTS.md`. It exists so a skeptic,
an auditor, or a competitor can reproduce every number and judge whether the
comparison is fair. If you find a way it is *not* fair, open an issue — the
corpus and harness are committed precisely so the claims can be contested.

## What this benchmark does and does not claim

**Claims (and how they are supported):**
1. **Domain coverage** — which governance domains a tool can surface findings in
   *at all*. Supported by running each tool on one shared corpus and grouping
   Valqore's findings by domain, plus a capability matrix.
2. **Convergence** — Valqore returns a single 0–100 score, one verdict, and
   machine-readable OSCAL evidence in one pass. Supported by the live run.

**Explicitly NOT claimed:**
- That Valqore finds *more issues* than a dedicated scanner in that scanner's own
  domain. Raw counts are **not comparable** across tools (see "Why counts are not
  comparable").
- That the capability matrix rows for tools not installed in a given run were
  re-verified that run. Those rows are sourced from the 2026 competitive review
  and **clearly marked** when the tool was skipped (see the Provenance block in
  `RESULTS.md`).

## The corpus

`corpus/` is a small, deliberately messy, *committed* repository — Kubernetes
manifests + one Terraform file + one Dockerfile — designed to be **fair to
rivals**, not to flatter Valqore:

- **Bread-and-butter misconfigs every scanner should catch** (privileged
  container, `:latest` tag, missing `securityContext`, `0.0.0.0/0` ingress,
  public/unencrypted S3, root Dockerfile user). Rivals get full credit for these.
- **Cost waste** (a 10×-over-provisioned batch worker; a 4×GPU inference deploy
  with no limits) — invisible to pure security scanners.
- **Ungoverned AI** (an LLM/agent workload with no auth, no risk classification,
  no rate limit, a hardcoded API key).
- **Compliance + carbon** gaps that only surface when those domains are evaluated.

Every corpus file is SHA-256 hashed in the Provenance block of each run, so you
can confirm you scanned identical inputs.

## How each tool is invoked

All tools run against the **same directory** with no Valqore-favouring flags:

| Tool | Command | What we count as a "finding" |
|---|---|---|
| Valqore | `valqore evaluate corpus/ --score -o json` | rule results with `outcome == FAIL` (excludes PASS, WARN, and `NOT_ASSESSED`) |
| Checkov | `checkov -d corpus/ --compact -o json` | sum of `summary.failed` across check types |
| Kubescape | `kubescape scan corpus/ --format json` | failed controls (failed-resource count) |
| Trivy | `trivy config corpus/ --format json` | `Misconfigurations` across results |
| kube-score | `kube-score score --output-format json *.yaml` | checks with grade < 10 (not OK), excluding skipped |

A competitor is only reported when its binary is on `PATH`; otherwise the run
marks it "not installed" and the capability-matrix row carries the documented
caveat. Checkov must be installed in its **own** environment (pipx / separate
venv) — it pins an old `python-hcl2` that conflicts with Valqore's Terraform
parser — so the harness only invokes a standalone `checkov` on `PATH`.

## Why counts are not comparable

Different tools have different rule granularity: one tool may emit a single
finding for "pod is insecure" where another emits five (no `runAsNonRoot`, no
`readOnlyRootFilesystem`, no dropped capabilities, …). A larger number is
therefore **not** automatically "better." For this reason the benchmark leads
with *domain coverage* and *convergence*, and presents per-tool counts only
within each tool's own scope — never as a cross-tool leaderboard.

## Reproducibility

```bash
pipx install checkov                         # isolated; de-facto OSS IaC baseline
# brew install kubescape trivy kube-score    # optional K8s scanners
VALQORE_LICENSE_SKIP=true python benchmarks/run_benchmark.py
```

Each run writes:
- `RESULTS.md` — the human-readable report (committed snapshot).
- `results.json` — full structured output incl. provenance (git-ignored; per-run).

The Provenance block records the UTC timestamp, the corpus SHA-256, and the
exact version string of every tool that ran. Same corpus hash + same tool
versions ⇒ same numbers.

## Known limitations / how to make it fairer

- **Coverage, not parity-of-depth.** This shows *what each tool can see*, not a
  rule-by-rule depth comparison within the security domain. A future iteration
  could map specific overlapping findings (e.g. "both flag the privileged pod")
  to demonstrate parity, not just breadth.
- **Capability-matrix rows for skipped tools are review-sourced**, not re-run.
- **Small corpus.** It is intentionally small and legible; it is not a
  statistically representative sample of real-world repositories.
- Contributions that add rival adapters, enlarge the corpus, or challenge a
  capability-matrix cell are welcome — that is the point of committing it.
