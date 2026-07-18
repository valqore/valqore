# Vendor security & due-diligence FAQ

A self-serve answer to the questions a security or procurement team asks before
adopting Valqore — mapped to the items you'd find on a SIG Lite / CAIQ / standard
vendor questionnaire. It is deliberately specific and honest about what is in
place versus planned. For anything not covered, email **tunc@valqore.io** and
we'll answer in writing.

> **The one-paragraph version.** Valqore is **self-hosted software** — a container,
> CLI, Kubernetes admission webhook, or MCP gate that runs **entirely inside your
> environment**. There is no Valqore-operated SaaS that processes your data, so
> most "vendor cloud" questions (subprocessors, data residency, multi-tenancy,
> their SOC 2) don't apply the way they do for a hosted service: **the boundary is
> yours.** It is read-only, makes no outbound calls, and runs fully air-gapped.

---

## 1. Company & product

| Question | Answer |
|---|---|
| What is Valqore? | A deterministic infrastructure-governance engine. It evaluates Kubernetes manifests, Terraform, and live cloud/cluster state against 1,379+ versioned rules (security, cost, carbon, AI governance, compliance) and returns a score, a verdict (PASS / PASS_WITH_MONITORING / BLOCK), and machine-readable evidence. |
| Delivery model | **Self-hosted only.** Distributed as a signed OCI image (`ghcr.io/valqore/engine:latest`). There is no hosted/SaaS product that ingests customer data. |
| Where does it run? | In your environment: as a CLI, a CI/CD step, a Kubernetes operator/admission webhook, or an MCP gate. |
| Open source? | The engine is distributed as a **compiled image** (no readable source). The public showcase, examples, trust docs, and benchmark are public at `github.com/valqore/valqore`. |

## 2. Data handling & privacy

| Question | Answer |
|---|---|
| What customer data does Valqore access? | Infrastructure **configuration** you point it at — manifests, Terraform, and (for live scans) read-only resource metadata via your own cloud credentials. It does not need application data, PII, or secrets to function. |
| Where is data processed? | **In your environment.** Nothing is sent to Valqore. There is no Valqore-operated cloud in the data path. |
| Does Valqore phone home / send telemetry? | **No.** Zero telemetry, no usage beacons, no outbound calls in the deterministic core. It runs fully air-gapped. |
| Data residency | Entirely under your control — Valqore runs wherever you run it. There is no cross-border transfer because data never leaves your boundary. |
| What is stored, and where? | Your license key, the signed approval/audit journal, and learned baselines live on a volume **you** control (`~/.valqore` / the mounted `valqore-data` volume). Retention and deletion are yours to set; delete the volume and nothing remains. |
| Does it modify our infrastructure? | **No — read-only by design.** Live cloud access reads configuration; Valqore never creates, modifies, or deletes resources. The admission/agent gates *block* unsafe changes; they don't apply changes. |
| PII / sensitive data | The core processes config, not user data. When the optional cloud-AI explanation is enabled (off by default), only rule IDs and severity counts are sent — never raw manifests, names, IPs, or secrets — and PII is sanitized first. The embedded offline model avoids any external call entirely. |

## 3. Subprocessors & third parties

| Question | Answer |
|---|---|
| Do you use subprocessors that touch our data? | For the **self-hosted product: none.** Valqore has no cloud that receives your data, so there are no data subprocessors. |
| Optional integrations you control | If *you* enable a cloud LLM for explanations (Azure OpenAI / Anthropic / OpenAI), that provider is *your* subprocessor under *your* keys — and only rule IDs/severity are sent. The default embedded model removes even that. |
| Marketing site | `valqore.io` uses Resend for the contact form and Azure App Service for hosting. These touch **website** enquiries only — never the product or your infrastructure. |

## 4. Architecture, access & authentication

| Question | Answer |
|---|---|
| How does Valqore authenticate to our cloud? | Using **your existing** AWS / Azure / GCP / kubeconfig credential chain — read-only. Recommended scope is a read-only role (e.g. AWS `ReadOnlyAccess` or `*:Describe*` + `ce:GetCostAndUsage`). Valqore stores no cloud credentials. |
| Inbound access from Valqore? | None. There is no Valqore-side service that connects into your environment. |
| Access control within Valqore | Enterprise adds RBAC (roles, permissions), SSO (SAML/OIDC), and SCIM. The free tier runs as a local tool under your own host/cluster auth. |
| Licensing | Self-hosted with an offline-capable, HMAC-signed license key — no license server callback required. |

## 5. Encryption

| Question | Answer |
|---|---|
| In transit | All processing is local; when you enable live cloud scans, traffic uses the cloud SDKs' standard TLS to *your* providers. There is no Valqore endpoint to encrypt to. |
| At rest | The local data volume is under your control and can sit on your encrypted storage / KMS. |
| Image integrity | Every published image is cryptographically signed (Sigstore keyless, GitHub OIDC + Rekor) and ships an SPDX SBOM. |
| Cryptographic posture | Valqore itself *checks* crypto posture (post-quantum / CNSA 2.0 pack) and ships a tamper-evident, HMAC-signed approval/audit journal. |

## 6. Supply-chain security

| Question | Answer |
|---|---|
| Can we verify what we run? | Yes. Verify the signature and SBOM before running — see **["Verify image authenticity"](README.md#verify-image-authenticity-supply-chain)**: `cosign verify` + `cosign verify-attestation --type spdxjson`. |
| Provenance | Signed in CI via Sigstore keyless (GitHub OIDC), logged to the Rekor transparency log. |
| Do you eat your own dog food? | Yes — our images ship signed with SBOM attestations, the supply-chain governance we enforce on customers. |

## 7. Secure development & vulnerability management

| Question | Answer |
|---|---|
| Vulnerability disclosure | A coordinated-disclosure policy with safe harbor — see **[SECURITY.md](SECURITY.md)**. Private reporting via GitHub advisories or `tunc@valqore.io`. |
| Response targets | Acknowledge within **3 business days**; initial assessment + severity within **10 business days**; coordinated public disclosure after a fix. |
| Bug bounty | Not yet a paid program; we credit reporters publicly. SECURITY.md will say so if that changes. |
| Dependencies | Tracked via the SBOM; security fixes ship on the latest released minor version. |
| Testing | The engine ships with ~2,880 automated tests run in CI. |

## 8. Compliance & certifications

| Question | Answer |
|---|---|
| Certifications held | We will not claim certifications we don't hold. **Valqore is not SOC 2 certified yet** — SOC 2 Type II controls and evidence are being assembled. |
| Frameworks Valqore *maps to* | 16 compliance packs — HIPAA, SOC 2, PCI-DSS, GDPR, ISO 27001, ISO/IEC 42001, EU AI Act, NIST CSF, NIST AI RMF, OWASP LLM, OWASP Agentic, DORA, FedRAMP, SR 11-7, CRA, PQC Migration — each exportable as machine-readable **NIST OSCAL 1.1.2** evidence. (This is what the product *produces for you*, distinct from certifications *we* hold.) |
| FedRAMP | Valqore provides FedRAMP-**aligned** controls and OSCAL evidence you run inside your own boundary; it is not itself a FedRAMP-authorized service. |
| Honest posture | See **[TRUST.md](TRUST.md)** for the full in-place-vs-planned list, and **[valqore.io/security](https://valqore.io/security)**. |

## 9. AI / ML specifics

| Question | Answer |
|---|---|
| Does an LLM make governance decisions? | **No.** Verdicts come from a deterministic rule engine — the same input yields the same verdict, which is what makes it admissible as evidence. The optional model only phrases explanations; it can never change a verdict (the "sealed loop"). |
| Do you train on our data? | No. The embedded model is pre-trained and runs **offline, in your container**; your code and config are never used for training and never leave the container. |
| AI governance of *your* agents | Valqore governs the AI agents in *your* infrastructure (agent-audit / agent-gate) — that's a product feature, not a data-handling concern. |

## 10. Business continuity & availability

| Question | Answer |
|---|---|
| Availability dependency on Valqore? | **None at runtime.** Because Valqore is self-hosted (and Kubernetes admission can compile to **native ValidatingAdmissionPolicy**), enforcement keeps working even if Valqore the company is unreachable. There is no Valqore SaaS whose outage affects you. |
| Vendor lock-in / exit | Evidence is standards-based (NIST OSCAL); rules and verdicts are reproducible and self-hosted. Stop the container and nothing remains running. |

---

### Still need something specific?

Send your questionnaire (SIG, CAIQ, custom) to **tunc@valqore.io**. We'd rather
answer a hard question in writing than lose your trust to a vague one. For
hands-on review, you can verify the signed image, run the
[public benchmark](benchmarks/), and scan your own cluster — all without anything
leaving your network.

_Last updated: 2026-06-29. This document describes the self-hosted Valqore engine;
it is informational and not a contract._
