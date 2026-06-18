# Valqore

> **One scan. One score. One verdict.**

[![Website](https://img.shields.io/badge/website-valqore.io-blue)](https://www.valqore.io)
[![Docker](https://img.shields.io/badge/docker-valqore%2Fengine-2496ED?logo=docker)](https://hub.docker.com/r/valqore/engine)
[![Rules](https://img.shields.io/badge/rules-1,370-brightgreen)]()
[![Compliance Packs](https://img.shields.io/badge/compliance%20packs-16-blueviolet)]()
[![Blog](https://img.shields.io/badge/blog-blog.valqore.io-black)](https://blog.valqore.io)

---

Valqore is an infrastructure governance engine that scans Kubernetes manifests, Terraform configurations, and cloud resources — then returns a **score (0-100)** and a **verdict** (PASS, PASS_WITH_MONITORING, or BLOCK).

**1,370 built-in rules** across security, cost, **carbon/sustainability (GreenOps)**, compliance, and AI governance, organised into **16 compliance packs** (including OWASP Top 10 for Agentic Applications 2026, EU AI Act Annex III, CRA, DORA, SOC2, HIPAA, FedRAMP, SR 11-7, and PQC Migration / CNSA 2.0). No configuration needed. Runs anywhere Docker runs.

## Five ways to run Valqore

| Surface | Install | Best for |
|---|---|---|
| **CLI / Docker** | `docker run valqore/engine:1.5.0 evaluate manifest.yaml` | Local checks, CI pipelines |
| **K8s admission control** | `helm install` from [`valqore-stack`](https://github.com/valqore/valqore-operator/tree/main/charts/valqore-stack) | Cluster-wide enforcement via native `ValidatingAdmissionPolicy` |
| **VS Code extension** | [`valqore-vscode`](https://github.com/valqore/valqore-vscode) `.vsix` | Real-time CodeLens + hover + quick-fix in YAML / Terraform / Helm |
| **Freelens K8s IDE** | [`freelens-valqore`](https://github.com/valqore/freelens-valqore) extension | Resource-detail panels + cluster overview + right-click policy checks |
| **MCP for Claude / Cursor** | `valqore mcp` | 134 governance tools your AI assistant can call |

## 30-second cluster install (Kubernetes-native)

```bash
# 1. Install the Valqore CRDs
kubectl apply -f https://raw.githubusercontent.com/valqore/valqore-engine/master/valqore/k8s/crds.yaml

# 2. Install the operator stack (Go controller-runtime, ~30 MB image)
helm install valqore oci://ghcr.io/valqore/charts/valqore-stack \
  --namespace valqore-system --create-namespace \
  --set 'policies[0].name=enforce-owasp-agentic' \
  --set 'policies[0].pack=owasp_agentic' \
  --set 'policies[0].action=Warn'
```

Within 30 seconds, **8 native `ValidatingAdmissionPolicy` objects** materialise on the cluster — the K8s API server enforces them. **Valqore is not in the data path.**

```bash
kubectl get valqorepolicy enforce-owasp-agentic
# NAME                    PACK            ACTION   READYVAPS
# enforce-owasp-agentic   owasp_agentic   Warn     8
```

Flip `action: Warn` → `action: Deny` when you're confident, then watch the API server reject unannotated agent workloads at admission time.

**Key differentiators:**
- **GreenOps built-in** — CO2e emissions per workload, greener region suggestions, carbon budgets, GPU emissions tracking. 77 cloud regions with grid carbon intensity data.
- **AI Scan** — one command runs evaluate + drift detection + AI-powered explanation. The AI image includes a fine-tuned model that runs fully offline — your code never leaves the container.
- **Interactive chat** — ask Valqore questions about your scan results in natural language. Get remediation advice, compliance mapping, and cost optimization tips through a conversational interface.
- **AI Governance** — detect ungoverned AI/ML workloads, enforce EU AI Act compliance, and gate model promotions to production.
- **AI agent fleet governance** — `agent-audit` discovers the AI agents already running in your manifests, cluster, or cloud and scores each one's governance posture across five dimensions, then rolls up to a GOVERNED / PARTIAL / UNGOVERNED fleet verdict and exports it as auditor-ready OSCAL. The answer to "who governs the agents now governing your infra?"

---

## Installation

### Requirements

- Docker (any OS — Linux, macOS, Windows)
- A Valqore license key ([request a trial](mailto:tunc@valqore.io))

### Step 1: Pull the image

```bash
docker pull valqore/engine:1.5.0
```

Two variants available:

| Image | Size | Description |
|-------|------|-------------|
| `valqore/engine:1.5.0` | 626 MB | Standard — all 1,370 rules, scoring, drift, billing, compliance |
| `valqore/engine:1.5.0-ai` | 2.5 GB | Everything above + embedded AI model for offline explanations |

### Step 2: Create a persistent volume

```bash
docker volume create valqore-data
```

This stores your license. Use `-v valqore-data:/home/valqore/.valqore` on every run.

### Step 3: Activate your license

```bash
docker run --rm -v valqore-data:/home/valqore/.valqore \
  valqore/engine:1.5.0 activate YOUR_LICENSE_KEY
```

Output:
```
License activated!
  Email:   your@email.com
  Plan:    trial
  Expires: 2026-05-15 (30 days remaining)
```

### Step 4: Scan your first file

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 evaluate /workspace/deploy.yaml --score
```

Output:
```
Valqore Score: 84/100 (Grade: B)
  Security: 78 | Reliability: 77 | Cost: 90 | Carbon: 97 | Compliance: 100
Cost estimate: $19.53/mo (aws, us-east-1)

Verdict: BLOCK

Total: 495 | Pass: 383 | Warn: 84 | Fail: 28
```

That's it. You're scanning infrastructure.

---

## Verify image authenticity (supply chain)

Every published image is cryptographically signed and carries an SPDX SBOM, so you can prove exactly what you're running. Install [cosign](https://docs.sigstore.dev/cosign/system_config/installation/), then:

**Standard image** (`valqore/engine:1.5.0`) — keyless-signed in CI via Sigstore (GitHub OIDC + Rekor):

```bash
cosign verify valqore/engine:1.5.0 \
  --certificate-identity-regexp 'https://github.com/valqore/valqore-engine/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

**AI image** (`valqore/engine:1.5.0-ai`) — signed with Valqore's release key ([`cosign.pub`](cosign.pub)):

```bash
cosign verify --key cosign.pub --insecure-ignore-tlog valqore/engine:1.5.0-ai
cosign verify-attestation --key cosign.pub --insecure-ignore-tlog --type spdxjson valqore/engine:1.5.0-ai
```

Both checks confirm the image hasn't been tampered with since publish. The SBOM (SPDX) enumerates every component in the image for vulnerability scanning and audit.

---

## Security & trust

- **[TRUST.md](TRUST.md)** — how the deterministic engine decides, what Valqore does (and doesn't) do with your data, self-hosted/no-egress posture, supply-chain integrity, and an honest in-place-vs-planned status.
- **[SECURITY.md](SECURITY.md)** — coordinated vulnerability disclosure policy, private reporting channels, response targets, and safe harbor.

---

## What You Can Do

### Scan Kubernetes manifests

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 evaluate /workspace/kubernetes/ --score
```

### Scan Terraform files

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 evaluate /workspace/main.tf --score
```

### Scan an entire directory

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 evaluate /workspace/ --score
```

### Cost simulation — what if we migrate to Graviton?

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 what-if /workspace/deploy.yaml --graviton
```

Output:
```
=== What-If: Migrate to Graviton (ARM) ===
  Cost:    $19/mo -> $15/mo (-20%)
  Carbon:  0.29 kg -> 0.09 kg (-69.5%)
```

### Cost simulation — what if we use spot instances?

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 what-if /workspace/deploy.yaml --spot-ratio 70
```

### Check cloud billing (AWS)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  valqore/engine:1.5.0 finops billing --cloud aws --daily --days 30
```

Output:
```
AWS Daily Cost Trend (last 30 days)  Total: $3,459.14

      $137 |                 #
      $120 |####             ##########
      $103 |#####           #############
       $86 |#############################
           +------------------------------
            03-17                    04-15
```

### Check cloud billing (Azure)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -e AZURE_CLIENT_ID=$AZURE_CLIENT_ID \
  -e AZURE_TENANT_ID=$AZURE_TENANT_ID \
  -e AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET \
  valqore/engine:1.5.0 finops billing --cloud azure \
    --subscription-id YOUR_SUBSCRIPTION_ID --daily
```

### Budget gate for CI/CD

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  valqore/engine:1.5.0 finops billing --cloud aws --fail-if-over 5000
```

Exit code 1 if monthly spend exceeds $5,000 — use this in CI/CD to block deploys when costs spike.

### Detect infrastructure drift

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  valqore/engine:1.5.0 drift-state /workspace/terraform.tfstate --cloud aws --attribution
```

Shows what changed, when, and who changed it (via CloudTrail).

### Continuous drift monitoring with Slack alerts

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  valqore/engine:1.5.0 drift-state /workspace/terraform.tfstate \
    --watch --interval 30 \
    --slack https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### AI governance gate

Block ungoverned AI/ML workloads from reaching production:

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 ai-gate /workspace/
```

Output:
```
=== AI Promotion Gates: ml-inference -> production ===
  AI Registered:            FAIL
  Human Oversight:          FAIL
  EU AI Act Classification: FAIL
  Kill Switch:              FAIL
  Result: BLOCKED -- 4 of 5 gates failing
```

### AI agent fleet governance audit

Score the governance posture of every AI agent in your manifests, cluster, or cloud:

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 agent-audit /workspace/
```

Output:
```
=== AI Agent Governance Posture ===
  Fleet: 2 agent(s) -- UNGOVERNED -- 0 governed / 2 with gaps -- avg score 45.9/100

  Agent                 Identity  Guardrails  Boundary  Oversight  Supply Chain
  research-agent (ai)   FAIL      FAIL        --        FAIL       PASS
  ops-agent (ai)        PASS      FAIL        FAIL      --         PASS
```

Add `--format oscal -o agentgov.json` for an auditor-ready evidence pack where each dimension maps to a control.

### Shift-left cost gate

Block a change in CI before deploy on a $/mo ceiling or a delta-vs-baseline:

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 finops cost-gate /workspace/proposed/ \
    --baseline /workspace/current/ --max-delta 500
```

Exit code 1 when the change adds more than $500/mo over the baseline — cost *prevention* in the PR, not a dashboard after the bill lands.

### Container image audit

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 image-audit /workspace/ --check-updates
```

Output:
```
  redis     latest  ->  --       UNPINNED   HIGH
  nginx     1.21    ->  1.27.0   OUTDATED   HIGH
```

### Compliance evidence

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0 evidence hipaa -f /workspace/
```

All 16 packs: `hipaa`, `soc2`, `pci_dss`, `gdpr`, `iso27001`, `iso_42001`, `eu_ai_act`, `nist_csf`, `nist_ai_rmf`, `owasp_llm`, `owasp_agentic`, `dora`, `fedramp`, `sr_11_7`, `cra`, `pqc_migration`. Add `-f oscal` to any pack for machine-readable NIST OSCAL evidence.

### GreenOps — carbon tracking

Every `evaluate --score` includes carbon estimates automatically:

```
Carbon: 0.182 kg CO2e/mo (aws:us-east-1)
```

Valqore tracks CO2e emissions per workload using grid carbon intensity data across 77 cloud regions. It suggests greener regions, enforces carbon budgets, and tracks GPU embodied emissions. The what-if commands show carbon impact too:

```
=== What-If: Migrate to Graviton (ARM) ===
  Carbon:  0.29 kg -> 0.09 kg (-69.5%)
```

### AI-powered scan (evaluate + drift + explanation)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  valqore/engine:1.5.0-ai ai-scan /workspace/ \
    --state /workspace/terraform.tfstate --cloud aws
```

One command does everything: evaluates your manifests, detects drift against live cloud, and generates an AI-powered explanation with prioritized remediation steps. Uses the embedded fine-tuned model — your code never leaves the container, no API calls, fully offline.

Output:
```
Valqore AI Scan

Step 1/3: Evaluating manifests...
  Score: 84/100 (B) | Verdict: BLOCK
  Rules: 495 | Fail: 28 | Warn: 84

Step 2/3: Detecting drift...
  3 resources drifted

Step 3/3: Generating AI analysis...

  ## Key findings:
  - SP-007: Container running in privileged mode -- full host access
  - NET-012: LoadBalancer without NetworkPolicy on backend
  - CC-153: Missing cost allocation tags

  ## Remediation:
  1. Remove privileged: true and add capabilities.drop: ['ALL']
  2. Create NetworkPolicy restricting ingress to port 8080
  3. Add cost-center, team, environment labels
```

### Chat — ask questions about your infrastructure

```bash
docker run --rm -it \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.5.0-ai chat /workspace/deploy.yaml
```

Start an interactive conversation about your scan results:

```
You: What are the most critical issues?
Valqore: You have 2 CRITICAL findings that must be fixed immediately:
  1. SP-007: Container 'api' is running in privileged mode...
  2. NET-012: LoadBalancer without NetworkPolicy...

You: How do I fix the privileged container?
Valqore: Remove privileged: true and add a restrictive security context:
  securityContext:
    privileged: false
    runAsNonRoot: true
    allowPrivilegeEscalation: false
    capabilities:
      drop: ["ALL"]

You: Is this HIPAA compliant?
Valqore: Your current configuration fails 1 of 7 HIPAA controls...
```

The chat uses the embedded fine-tuned AI model. Everything runs locally inside the container — no data leaves your machine.

### Check license status

```bash
docker run --rm -v valqore-data:/home/valqore/.valqore \
  valqore/engine:1.5.0 license
```

---

## Cloud Provider Setup

Valqore is **read-only**. It never creates, modifies, or deletes resources.

### AWS

Pass credentials as environment variables:

```bash
-e AWS_ACCESS_KEY_ID=AKIA...
-e AWS_SECRET_ACCESS_KEY=...
-e AWS_DEFAULT_REGION=us-east-1
```

Minimum permissions: `ReadOnlyAccess` or custom policy with `ec2:Describe*`, `s3:GetBucket*`, `rds:Describe*`, `iam:List*`, `ce:GetCostAndUsage`, `cloudtrail:LookupEvents`.

### Azure

Pass service principal credentials:

```bash
-e AZURE_CLIENT_ID=your-app-id
-e AZURE_TENANT_ID=your-tenant-id
-e AZURE_CLIENT_SECRET=your-secret
```

Minimum roles: `Reader` + `Cost Management Reader`.

### Kubernetes

Mount your kubeconfig:

```bash
-v ~/.kube/config:/home/valqore/.kube/config:ro
```

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Valqore Gate
  run: |
    docker run --rm \
      -v ${{ github.workspace }}:/workspace \
      -v valqore-data:/home/valqore/.valqore \
      valqore/engine:1.5.0 evaluate /workspace/ --score --fail-on block
```

Exit code 1 on BLOCK verdict = PR fails.

### Cost gate in pipeline

```yaml
- name: Cost Gate
  run: |
    docker run --rm \
      -v valqore-data:/home/valqore/.valqore \
      -e AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }} \
      -e AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }} \
      valqore/engine:1.5.0 finops billing --cloud aws --fail-if-over 5000
```

---

## Try It — Example Scenarios

Clone this repo and scan any folder. Each scenario contains realistic infrastructure with intentional misconfigurations.

```bash
git clone https://github.com/valqore/valqore.git
cd valqore

docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd)/examples:/workspace \
  valqore/engine:1.5.0 evaluate /workspace/ecommerce/ --score
```

### Basics — Secure vs Insecure

| File | Score\* | What Valqore catches |
|------|--------|---------------------|
| [basics/insecure-deploy.yaml](examples/basics/insecure-deploy.yaml) | 28 / F · BLOCK | Privileged container, unpinned image, no NetworkPolicy |
| [basics/secure-deploy.yaml](examples/basics/secure-deploy.yaml) | 76 / C · **PASS**† | Hardened + full governance annotations (CRA/DORA/rollback) — zero criticals |
| [basics/insecure-terraform.tf](examples/basics/insecure-terraform.tf) | 46 / F · BLOCK | Public RDS, open security group, unencrypted S3 |
| [basics/secure-terraform.tf](examples/basics/secure-terraform.tf) | 70 / C · BLOCK | Encrypted, private, Graviton, DynamoDB locking |
| [basics/ai-workload.yaml](examples/basics/ai-workload.yaml) | AI gate: BLOCK | Ungoverned GPU workload |
| [basics/gpu-ml-training.yaml](examples/basics/gpu-ml-training.yaml) | AI gate: PASS | Proper AI governance annotations |
| [basics/microservices-stack.yaml](examples/basics/microservices-stack.yaml) | 10 / F · BLOCK | Hardcoded secrets, no limits, privileged |

\*Scores reflect Valqore's **strict default policy** — most real-world workloads BLOCK until hardened. The point of each pair is the *relative* improvement.

†**PASS under a policy.** The default verdict is deliberately strict (it blocks on any finding). Real teams set a risk-appropriate bar in [`examples/.valqore/policy.yaml`](examples/.valqore/policy.yaml) — here: block on CRITICAL + require a passing score, treat HIGH as must-fix-soon. Under that policy the hardened workload **passes** and the insecure one still **blocks**:

```bash
# secure-deploy → PASS (76/100, zero criticals)
docker run --rm -v $(pwd):/workspace valqore/engine:1.5.0 \
  env-evaluate /workspace/examples/basics/secure-deploy.yaml \
  -e prod --policy /workspace/examples/.valqore/policy.yaml

# insecure-deploy → BLOCK (28/100, 3 criticals)
docker run --rm -v $(pwd):/workspace valqore/engine:1.5.0 \
  env-evaluate /workspace/examples/basics/insecure-deploy.yaml \
  -e prod --policy /workspace/examples/.valqore/policy.yaml
```

### Real-World Scenarios

| Scenario | Path | What's Inside |
|----------|------|--------------|
| E-Commerce | [examples/ecommerce/](examples/ecommerce/) | Storefront + payment + DB. Hardcoded Stripe keys, privileged payment service, public RDS. |
| SaaS Platform | [examples/saas-platform/](examples/saas-platform/) | API gateway + auth + workers. JWT secrets in plain text, no tenant isolation. |
| Data Pipeline | [examples/data-pipeline/](examples/data-pipeline/) | Kafka + Spark + Elasticsearch. AWS creds hardcoded, Spark as root, data on emptyDir. |
| Startup MVP | [examples/startup-mvp/](examples/startup-mvp/) | Node.js + MongoDB in one pod. DB password in env, default namespace, NodePort. |
| Fintech Trading | [examples/fintech/](examples/fintech/) | Matching engine + market feed + risk calc. Privileged engine, single-AZ DB, no encryption. |
| Azure Web App | [examples/azure/](examples/azure/) | App Service + SQL + Storage. TLS 1.0, public SQL, secrets in app settings. |
| GCP GKE | [examples/gcp/](examples/gcp/) | GKE + Cloud SQL + Firewall. Legacy ABAC, public DB, allow-all firewall. |

### GreenOps Scenarios

Compare carbon impact — same workload, different configurations:

| File | What It Shows |
|------|--------------|
| [greenops/high-carbon-deployment.yaml](examples/greenops/high-carbon-deployment.yaml) | 10 GPU replicas + 20 batch workers in us-east-1. High carbon footprint, oversized resources. |
| [greenops/low-carbon-deployment.yaml](examples/greenops/low-carbon-deployment.yaml) | Right-sized, eu-north-1 (hydro/nuclear), carbon budget set, fewer replicas. |

```bash
# Compare the two
docker run --rm -v valqore-data:/home/valqore/.valqore \
  -v $(pwd)/examples:/workspace \
  valqore/engine:1.5.0 evaluate /workspace/greenops/high-carbon-deployment.yaml --score

docker run --rm -v valqore-data:/home/valqore/.valqore \
  -v $(pwd)/examples:/workspace \
  valqore/engine:1.5.0 evaluate /workspace/greenops/low-carbon-deployment.yaml --score
```

### AI Scan Scenarios

Full-stack app with K8s + Terraform — run `ai-scan` to get evaluate + drift + AI explanation in one shot:

| File | What It Shows |
|------|--------------|
| [ai-scan/multi-tier-app.yaml](examples/ai-scan/multi-tier-app.yaml) | Frontend + API + workers + DB + Redis. Hardcoded secrets, root user, AWS keys in env. |
| [ai-scan/infra.tf](examples/ai-scan/infra.tf) | EKS + RDS + S3 + IAM. Public EKS, unencrypted DB, admin IAM policy, open security group. |

```bash
# AI Scan — evaluates everything and explains findings
docker run --rm -v valqore-data:/home/valqore/.valqore \
  -v $(pwd)/examples:/workspace \
  valqore/engine:1.5.0-ai ai-scan /workspace/ai-scan/
```

### Chat Scenarios

Scan these files, then start a chat to ask questions — great for compliance-heavy environments:

| File | What It Shows |
|------|--------------|
| [chat/healthcare-api.yaml](examples/chat/healthcare-api.yaml) | Patient API + EHR integration + audit logger. HIPAA-relevant: secrets in env, privileged EHR connector, audit logs on emptyDir. |
| [chat/finserv-platform.yaml](examples/chat/finserv-platform.yaml) | Transaction processor + fraud ML + compliance reporter. PCI-DSS relevant: card encryption keys in env, privileged GPU fraud model. |

```bash
# Scan first, then chat about findings
docker run --rm -it -v valqore-data:/home/valqore/.valqore \
  -v $(pwd)/examples:/workspace \
  valqore/engine:1.5.0-ai chat /workspace/chat/healthcare-api.yaml

# Try asking:
#   "Is this HIPAA compliant?"
#   "What are the biggest risks?"
#   "How do I fix the secrets?"
#   "Generate a compliance report"
```

---

## What Valqore Covers

| Category | What It Does |
|----------|-------------|
| **Security** | Container hardening, RBAC, encryption, network policies, supply chain, attack path analysis |
| **Cost & FinOps** | Waste detection, right-sizing, billing analysis (AWS/Azure/GCP), budget gates, cost simulation |
| **GreenOps** | CO2e per workload, greener region suggestions, carbon budgets, GPU emissions, 77 regions with grid intensity data |
| **Compliance** | 16 packs: HIPAA, SOC 2, PCI-DSS, GDPR, EU AI Act, ISO 42001, NIST AI RMF, OWASP LLM/Agentic, CIS, DORA, FedRAMP, SR 11-7, CRA, PQC, and more — each exportable as machine-readable **NIST OSCAL** evidence |
| **AI Governance** | Shadow AI detection, EU AI Act risk classification, model promotion gates, GPU cost/carbon tracking |
| **AI Agent Fleet Governance** | `agent-audit` discovers AI agents across manifests/cluster/cloud and scores each one's posture (identity, guardrails, boundary, oversight, model supply chain) into a GOVERNED / PARTIAL / UNGOVERNED fleet verdict — exportable as OSCAL. Plus a runtime MCP gate for live agent tool calls |
| **Drift Detection** | Terraform state vs live cloud, CloudTrail attribution, continuous monitoring with Slack alerts |
| **AI Scan & Chat** | One-command scan with AI explanation, interactive chat for remediation advice — fully offline |
| **Multi-Cloud** | AWS, Azure, GCP, and any Kubernetes cluster. Read-only — never modifies your infrastructure |
| **Dashboard** | Web-based dashboard for visualizing scores, trends, and team-wide governance — *coming soon* |

---

## Blog

Technical deep-dives and real-world examples:
- [blog/](blog/) — code examples from published posts
- [blog.valqore.io](https://blog.valqore.io) — full articles

---

## Links

- Website: [valqore.io](https://www.valqore.io)
- Docker Hub: [valqore/engine](https://hub.docker.com/r/valqore/engine)
- Blog: [blog.valqore.io](https://blog.valqore.io)
- Book a demo: [calendly.com/tuncvalqore](https://calendly.com/tuncvalqore/30min)
- Contact: tunc@valqore.io

---

VALQORE is a pending trademark. All rights reserved. See [LICENSE](LICENSE).
