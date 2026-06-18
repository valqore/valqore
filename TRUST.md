# Trust & transparency

Valqore is a governance and enforcement gate. To be trusted with that role it has
to be transparent about how it works, what it does with your data, and what it
can and cannot prove today. This page is deliberately specific — and honest about
what is in place versus what is planned.

## How the engine decides (and why it's deterministic)

Valqore's verdict is produced by a **deterministic rule engine**, not by a
language model. The same input always produces the same score, verdict, and
findings — which is what makes the output suitable as compliance evidence.

- **Rules decide; AI only explains.** Each finding comes from an explicit,
  versioned rule (e.g. `SP-006`, `AIG-150`) evaluated against your manifests,
  Terraform, or live cloud/cluster state. The optional embedded model is used
  *only* to phrase explanations and remediation suggestions — it can never
  change a PASS/FAIL/BLOCK. We call this the sealed loop.
- **No probabilistic guardrail in the decision path.** There is no LLM-as-judge
  deciding whether your infrastructure is compliant. That is a design choice:
  regulators and auditors need reproducibility, not a model's opinion.
- **Honest about missing data.** When a rule needs telemetry it doesn't have
  (e.g. live utilisation for an over-provisioning check), it reports
  **`NOT_ASSESSED`** rather than a misleading PASS, and that count is shown
  separately. A scan never manufactures confidence it doesn't have.
- **Estimates are labelled.** Cost figures are clearly marked as static
  list-price estimates (not billed spend) and point you to live billing for
  actuals.

## What Valqore does with your data

- **Self-hosted. No SaaS. No data egress.** Valqore runs as a container, a CLI,
  an admission webhook, or an MCP gate **inside your environment**. It does not
  phone home, and there is no Valqore-operated cloud that sees your
  infrastructure, manifests, findings, or cloud credentials.
- **Cloud access is read-only and uses your own credentials.** Live scanning
  uses your existing AWS/Azure/GCP/kubeconfig credential chain. Valqore reads
  resource configuration; it does not create, modify, or delete your resources.
- **What's stored locally.** Your license key, the signed approval/audit journal,
  and learned baselines live on a volume *you* control
  (`~/.valqore` / the mounted `valqore-data` volume). Nothing leaves it.
- **Air-gap friendly.** The standard and `-ai` images run with no outbound
  network access. The embedded model means even AI explanations work offline.

## Supply-chain integrity

- **Signed images + SBOM.** Every published image is cryptographically signed and
  ships an SPDX SBOM. You can verify exactly what you're running with
  `cosign verify` / `cosign verify-attestation` — see
  ["Verify image authenticity"](README.md#verify-image-authenticity-supply-chain).
- **Reproducible benchmark.** Our competitive coverage claims are backed by a
  committed, reproducible benchmark (corpus + harness + methodology) so anyone
  can re-run and contest the numbers. See the engine's `benchmarks/`.

## Reporting security issues

See [SECURITY.md](SECURITY.md) for our coordinated-vulnerability-disclosure
policy, private reporting channels, response targets, and safe-harbor terms.

## Current posture — what's in place vs planned

We will not claim certifications we don't hold. As of this writing:

**In place today**
- Deterministic, reproducible engine with versioned rules.
- Fully self-hosted; no telemetry or data egress.
- Read-only cloud access via your own credentials.
- Cryptographically signed images with SBOM attestation.
- Tamper-evident, HMAC-signed approval/audit journal for gated actions.
- A coordinated vulnerability disclosure policy with safe harbor.
- A public, reproducible competitive benchmark.

**Planned / in progress (not yet achieved)**
- SOC 2 Type II readiness (controls and evidence are being assembled; we are
  **not** SOC 2 certified yet).
- Independent third-party security review of the engine.
- Named reference customers / design partners.

If any statement here is unclear or you need something specific for a vendor
review, email `tunc@valqore.io` — we would rather answer a hard question than
lose your trust to a vague one.
