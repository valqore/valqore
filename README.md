# Valqore

> **One scan. One score. One verdict.**

[![Website](https://img.shields.io/badge/website-valqore.io-blue)](https://www.valqore.io)
[![Docker](https://img.shields.io/badge/docker-valqore%2Fengine-2496ED?logo=docker)](https://hub.docker.com/r/valqore/engine)
[![Rules](https://img.shields.io/badge/rules-1,262-brightgreen)]()
[![Blog](https://img.shields.io/badge/blog-blog.valqore.io-black)](https://blog.valqore.io)

---

Valqore is an infrastructure governance engine that scans Kubernetes manifests, Terraform configurations, and cloud resources — then returns a **score (0-100)** and a **verdict** (PASS, PASS_WITH_MONITORING, or BLOCK).

1,262 built-in rules. No configuration needed. Runs anywhere Docker runs.

---

## Installation

### Requirements

- Docker (any OS — Linux, macOS, Windows)
- A Valqore license key ([request a trial](mailto:tunc@valqore.io))

### Step 1: Pull the image

```bash
docker pull valqore/engine:1.0.0
```

Two variants available:

| Image | Size | Description |
|-------|------|-------------|
| `valqore/engine:1.0.0` | 626 MB | Standard — all 1,262 rules, scoring, drift, billing, compliance |
| `valqore/engine:1.0.0-ai` | 2.5 GB | Everything above + embedded AI model for offline explanations |

### Step 2: Create a persistent volume

```bash
docker volume create valqore-data
```

This stores your license. Use `-v valqore-data:/home/valqore/.valqore` on every run.

### Step 3: Activate your license

```bash
docker run --rm -v valqore-data:/home/valqore/.valqore \
  valqore/engine:1.0.0 activate YOUR_LICENSE_KEY
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
  valqore/engine:1.0.0 evaluate /workspace/deploy.yaml --score
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

## What You Can Do

### Scan Kubernetes manifests

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evaluate /workspace/kubernetes/ --score
```

### Scan Terraform files

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evaluate /workspace/main.tf --score
```

### Scan an entire directory

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evaluate /workspace/ --score
```

### Cost simulation — what if we migrate to Graviton?

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 what-if /workspace/deploy.yaml --graviton
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
  valqore/engine:1.0.0 what-if /workspace/deploy.yaml --spot-ratio 70
```

### Check cloud billing (AWS)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  valqore/engine:1.0.0 finops billing --cloud aws --daily --days 30
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
  valqore/engine:1.0.0 finops billing --cloud azure \
    --subscription-id YOUR_SUBSCRIPTION_ID --daily
```

### Budget gate for CI/CD

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  valqore/engine:1.0.0 finops billing --cloud aws --fail-if-over 5000
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
  valqore/engine:1.0.0 drift-state /workspace/terraform.tfstate --cloud aws --attribution
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
  valqore/engine:1.0.0 drift-state /workspace/terraform.tfstate \
    --watch --interval 30 \
    --slack https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### AI governance gate

Block ungoverned AI/ML workloads from reaching production:

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 ai-gate /workspace/
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

### Container image audit

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 image-audit /workspace/ --check-updates
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
  valqore/engine:1.0.0 evidence hipaa -f /workspace/
```

Available packs: `hipaa`, `soc2`, `pci_dss`, `gdpr`, `eu_ai_act`, `nist_ai_rmf`, `owasp_llm`, `iso_42001`, `cis`, `dora`, `fedramp`, `nist_csf`

### AI-powered scan (evaluate + drift + explanation)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  valqore/engine:1.0.0-ai ai-scan /workspace/ \
    --state /workspace/terraform.tfstate --cloud aws
```

Runs evaluate + drift detection + AI explanation in one command. Uses the embedded fine-tuned model — no API calls, fully offline.

### Check license status

```bash
docker run --rm -v valqore-data:/home/valqore/.valqore \
  valqore/engine:1.0.0 license
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
      valqore/engine:1.0.0 evaluate /workspace/ --score --fail-on block
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
      valqore/engine:1.0.0 finops billing --cloud aws --fail-if-over 5000
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
  valqore/engine:1.0.0 evaluate /workspace/ecommerce/ --score
```

### Basics — Secure vs Insecure

| File | Expected Score | What Valqore Catches |
|------|---------------|---------------------|
| [basics/insecure-deploy.yaml](examples/basics/insecure-deploy.yaml) | ~84 (B) | Privileged container, unpinned image, no NetworkPolicy |
| [basics/secure-deploy.yaml](examples/basics/secure-deploy.yaml) | ~97 (A) | Hardened version of the same deployment |
| [basics/insecure-terraform.tf](examples/basics/insecure-terraform.tf) | ~71 (C) | Public RDS, open security group, unencrypted S3 |
| [basics/secure-terraform.tf](examples/basics/secure-terraform.tf) | ~95 (A) | Encrypted, private, Graviton, DynamoDB locking |
| [basics/ai-workload.yaml](examples/basics/ai-workload.yaml) | AI gate: BLOCK | Ungoverned GPU workload |
| [basics/gpu-ml-training.yaml](examples/basics/gpu-ml-training.yaml) | AI gate: PASS | Proper AI governance annotations |
| [basics/microservices-stack.yaml](examples/basics/microservices-stack.yaml) | ~55 (D) | Hardcoded secrets, no limits, privileged |

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

---

## What Valqore Covers

- **Security** — container hardening, RBAC, encryption, network policies, supply chain
- **Cost** — waste detection, right-sizing, FinOps governance, billing analysis, budget gates
- **Carbon** — CO2e tracking, greener region suggestions, 77 regions, GPU emissions
- **Compliance** — HIPAA, SOC 2, PCI-DSS, GDPR, EU AI Act, ISO 42001, NIST, CIS, and more
- **AI Governance** — AI workload detection, model promotion gates, EU AI Act risk classification
- **Drift** — Terraform state vs live cloud, change attribution, continuous monitoring
- **Multi-Cloud** — AWS, Azure, GCP, Kubernetes

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
