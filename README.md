# Valqore

> **The convergence platform for cloud governance. One scan. One score. One verdict.**

[![Website](https://img.shields.io/badge/website-valqore.io-blue)](https://www.valqore.io)
[![Rules](https://img.shields.io/badge/rules-1,262-brightgreen)]()
[![Status](https://img.shields.io/badge/status-Early%20Access-orange)]()
[![License](https://img.shields.io/badge/license-All%20Rights%20Reserved-red)](LICENSE)

---

## What is Valqore?

Valqore is a **scored infrastructure gate** that combines security, cost, carbon, and compliance analysis into a single deterministic verdict. Instead of stitching together separate tools for policy scanning, cost estimation, carbon tracking, and compliance mapping, Valqore converges them into one engine with **1,262 rules across 18 categories**.

Every evaluation produces a **Valqore Score (0-100)**, a composite metric across security, reliability, cost, carbon, and compliance. Unlike tools that autonomously modify infrastructure, Valqore does **not** act — it **validates**. It reads evidence, applies rules, and returns one of three verdicts:

| Verdict | Meaning |
|---|---|
| `PASS` | Change is safe. Proceed. |
| `PASS_WITH_MONITORING` | Change is conditionally safe. Deploy with heightened observability. |
| `BLOCK` | Change violates one or more safety or policy rules. Do not proceed. |

Every verdict is backed by a complete, immutable audit trail: the evidence collected, the rule version applied, and the reasoning behind the decision.

---

## The Problem

Cloud waste accounts for **up to one-third of enterprise cloud spend**. AI-powered automation promises to fix this — but it introduces new risks:

- Autonomous agents can misconfigure autoscalers, causing cost spikes or outages
- Infrastructure-as-Code changes can pass code review yet violate runtime safety policies
- Carbon and sustainability targets are invisible to most infrastructure pipelines
- Post-change regressions (OOMKilled pods, latency spikes, cost anomalies) are often discovered too late

Valqore sits in front of these workflows as a **policy enforcement layer** — deterministic, explainable, and zero-touch on your infrastructure.

---

## Key Capabilities

### 1,262 Deterministic Rules Across 18 Categories
Valqore evaluates infrastructure against a versioned, immutable rule set covering:

| Category | Rules | What It Covers |
|----------|-------|----------------|
| Compute Safety (CS) | 35 | Resource requests/limits, HPA/VPA, probes, PDB, pod security |
| Security Posture (SP) | 100 | Encryption, IAM, container hardening, supply chain, RBAC |
| Operational Hygiene (OH) | 55 | Tagging, backups, graceful shutdown, anti-affinity, observability |
| Cost & Capacity (CC) | 75 | Waste detection, right-sizing, reserved instances, FinOps governance |
| Network Security (NET) | 60 | NetworkPolicy, ingress TLS, security groups, public exposure |
| GreenOps (GR) | 20 | Carbon thresholds, region intensity, GPU utilisation |
| AWS (AWS) | 245 | S3, IAM, RDS, EC2, VPC, Lambda, ECS/EKS, KMS, CloudTrail |
| Azure (AZ) | 140 | Storage, SQL/Cosmos DB, VM/AKS, NSG/VNet, Key Vault, App Service |
| GCP (GCP) | 100 | GCS, GCE/GKE, Cloud SQL, BigQuery, IAM/KMS, Cloud Run |
| Kubernetes CIS (K8S) | 50 | API server, etcd, controller manager, RBAC, worker nodes |
| Dockerfile (DOC) | 50 | Base image, USER, HEALTHCHECK, multi-stage builds, secrets |
| CI/CD Pipeline (CICD) | 20 | Pipeline security, secret management, build integrity |
| Compliance (CMP) | 20 | Regulatory controls, policy enforcement, audit readiness |
| Supply Chain (SCS) | 25 | SBOM, dependency scanning, artifact signing, provenance |
| AI Governance (AIG) | 128 | AI workload discovery, EU AI Act compliance, model promotion gates |
| Terraform State (TF) | 14 | State backend encryption, locking, key validation, drift markers |
| Container Images (IMG) | 15 | Image provenance, tag pinning, registry allowlists, layer audit |
| GPU Governance (GPU) | 10 | GPU allocation limits, idle detection, sharing policies, carbon per GPU-hour |

See [docs/rule-engine.md](docs/rule-engine.md) for the full rule taxonomy.

### Valqore Score (0-100)
Every evaluation produces a composite score with sub-scores per category (Security, Reliability, Cost, Carbon, Compliance). Severity-weighted deductions and a grade system (A through F) make it easy to track posture over time and set quality gates.

### Cost Estimation and Right-Sizing Advisor
Static cost estimation from CPU/memory requests across Azure, AWS, and GCP with provider comparison. The Right-Sizing Advisor detects oversized resources and recommends optimal alternatives with exact $/month savings, powered by an offline pricing catalog covering 270+ SKUs across compute, databases, cache, storage, and managed Kubernetes.

### GreenOps — Carbon-Aware Infrastructure
Calculates estimated energy consumption and CO₂ emissions using a methodology aligned with the [Cloud Carbon Footprint](https://www.cloudcarbonfootprint.org/) project. Supports 77 regions with grid carbon intensity data (including real-time updates via Electricity Maps), greener region suggestions, carbon budget enforcement, GPU/embodied emissions, and confidence intervals.

See [docs/greenops.md](docs/greenops.md) for the full methodology.

### IaC Scanning (Terraform, Helm, Kustomize)
Parses Terraform HCL and plan JSON, renders Helm charts, and builds Kustomize overlays. Auto-detects IaC type from file structure. Maps cloud resources (AWS S3, Azure Storage, GCP buckets) to security rules.

### Auto-Remediation
Optionally returns fixed manifests alongside findings. 10 auto-fix rules that add security contexts, resource limits, and read-only filesystems. Opt-in only — never mutates originals.

### Supply Chain Security
Image vulnerability scanning (Trivy + Grype adapters), Cosign signature verification, SBOM attestation checks, registry allowlists, and CVE exception management with expiry dates.

### Drift Detection
Event-driven detection of configuration drift between declared IaC state and live running infrastructure. Attributes changes to users and automation, scores drift severity, and surfaces remediation paths. Integrates with cloud change feeds (AWS CloudTrail, Azure Activity Log, GCP Cloud Audit).

### Container Image Audit
Deep inspection of container images beyond basic vulnerability scanning. Validates image provenance, enforces tag pinning policies, audits layer composition, and checks registry allowlists. Integrates with supply chain security rules for end-to-end image governance.

### Compliance Mapping
Rules mapped to compliance controls across 15 frameworks: CIS Kubernetes Benchmark, CIS AWS/Azure/GCP, SOC 2, PCI-DSS v4.0, NIST 800-53, NIST 800-190, MITRE ATT&CK, NSA/CISA Hardening, FinOps Framework, GHG Protocol, ISO 14064, EU AI Act, NIST AI RMF, ISO/IEC 42001. 12 compliance packs including ISO 42001 for AI management systems.

### Multi-Cloud Support
Operates across **AWS, Azure, GCP** and any conformant Kubernetes cluster. Read-only by design — Valqore never modifies infrastructure.

### AI as Explainer, Not Decider (Sealed Loop)
AI generates **human-readable explanations** and **remediation suggestions** but never overrides deterministic rule outcomes. Supports Azure OpenAI, Anthropic Claude, and local AI via Ollama for fully offline operation. The sealed loop ensures AI proposals are validated by the rule engine before being shown to users.

### AI Governance Module
128 rules across 5 phases for governing AI/ML workloads at the infrastructure level. Detects TensorFlow, PyTorch, vLLM, Triton, and Ollama workloads. Enforces EU AI Act risk classification, bias testing, human oversight, and model versioning. Tracks GPU utilization, training carbon, and cost-per-inference. Includes AI model promotion gates (dev to staging to production) with mandatory approval workflows. Mapped to EU AI Act, NIST AI RMF, and ISO/IEC 42001.

### GPU Governance
Dedicated GPU resource governance with allocation limits, idle GPU detection, multi-tenancy sharing policies, and carbon-per-GPU-hour tracking. Prevents GPU hoarding and enforces fair scheduling across teams.

### Architecture Diagram Generation
Automatically generates Mermaid architecture diagrams from manifests with namespace subgraphs, color-coded health status, cost labels, carbon badges, and attack path visualization. Ships in GitHub PR comments as collapsible sections.

### Attack Path Analysis
Security graph analysis that detects toxic combinations (public + root, privileged + no NetworkPolicy, cluster-admin bindings). BFS traversal from entry points to high-value targets with blast radius estimation and exploitability scoring. Reduces security score via multiplier.

### Score Trending & Regression Detection
Track Valqore Score over time per source/repo. Detect regressions with configurable thresholds. Regression warnings appear in GitHub PR comments when score drops.

### MCP Server for AI Agent Integration
6-tool MCP server (evaluate, list rules, validate, scan, explain, diagram) with SSE, HTTP, and stdio transports. Enables AI agents and IDE extensions to interact with Valqore programmatically.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Valqore Control Plane                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Evidence    │  │  Rule Engine │  │  Verdict     │  │
│  │  Collector   │→ │  (Immutable) │→ │  & Audit Log │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│          ↑                                   ↓          │
│  ┌──────────────┐                  ┌──────────────────┐ │
│  │  Cloud APIs  │                  │  CI/CD / Slack / │ │
│  │  (read-only) │                  │  Teams / Webhook │ │
│  └──────────────┘                  └──────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for a full system design description.

---

## How It Works

1. **Evidence collection** — Valqore reads current infrastructure state using read-only API calls (no agents, no sidecars, no code injection). Supports Kubernetes manifests, Terraform HCL/plan, Helm charts, Kustomize, and Dockerfiles.
2. **Rule evaluation** — The rule engine evaluates the input against all applicable rules (1,262 total across 18 categories) with smart filtering for Terraform resources and computes per-rule outcomes.
3. **Scoring** — The Valqore Score engine computes a composite 0-100 score with sub-scores per category.
4. **Cost and carbon assessment** — Estimates $/month cost across providers and CO₂e impact per region.
5. **Right-sizing** — Identifies over-provisioned resources and recommends optimal alternatives with savings.
6. **Decision delivery** — The verdict, score, findings, cost/carbon data, and AI-generated remediation are delivered via API, CLI, GitHub Action PR comment, or MCP server.
7. **Audit persistence** — Every decision is stored with its full evidence bundle and rule version for compliance.

See [docs/how-it-works.md](docs/how-it-works.md) for a detailed walkthrough.

---

## Use Cases

- **DevOps teams** — Block unsafe pull requests in GitHub Actions before they reach production. Auto-remediate common misconfigurations.
- **FinOps teams** — Enforce cost gates, detect over-provisioned resources, and surface right-sizing opportunities with $/month savings.
- **Platform engineering** — Apply consistent policy across multi-cluster, multi-cloud estates with a single score and verdict.
- **Security teams** — 1,262 rules covering CIS benchmarks, RBAC, network policies, supply chain, container hardening, and attack path analysis.
- **Sustainability / ESG** — Carbon-aware deployment decisions with 77-region support, real-time grid intensity, and CO₂e tracking.
- **AI-Ops / AIOps** — MCP server provides a safety layer that governs AI agent infrastructure changes through the sealed loop.
- **AI Governance** — 128 AIG rules detect shadow AI, enforce EU AI Act compliance, track GPU cost/carbon, and gate AI model promotions.
- **FinOps 2.0** — Advanced cost governance with anomaly detection, commitment utilization tracking, and unit economics per workload.

See [docs/use-cases.md](docs/use-cases.md) for detailed examples.

---

## Integrations

| Integration | Status |
|-------------|--------|
| REST API (FastAPI) | Shipped |
| CLI (Typer + Rich) | Shipped |
| GitHub Actions (PR gating + diagrams) | Shipped |
| GitLab CI | Shipped |
| Azure DevOps Pipelines | Shipped |
| Bitbucket Pipelines | Shipped |
| MCP Server (AI agents) | Shipped |
| Local AI via Ollama (fine-tuned) | Shipped |
| Pre-commit Hook | Shipped |
| VS Code Extension | Shipped |
| Kubernetes Admission Webhook | Planned |
| ArgoCD/Flux Pre-Sync Hook | Planned |

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full roadmap.

**Current status: Early Access — building in public.**

---

## Trademark

VALQORE is a pending trademark. USPTO Serial No. on file.

---

## Links

- Website: [valqore.io](https://www.valqore.io)
- Issues & Feedback: [GitHub Issues](https://github.com/valqore/public/issues)

---

## Contributing

We welcome discussion, feedback, and early adopter interest. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

All rights reserved. See [LICENSE](LICENSE) for details.
