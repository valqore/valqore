# Valqore

> **One scan. One score. One verdict.**

[![Website](https://img.shields.io/badge/website-valqore.io-blue)](https://www.valqore.io)
[![Docker](https://img.shields.io/badge/docker-valqore%2Fengine-2496ED?logo=docker)](https://hub.docker.com/r/valqore/engine)
[![Rules](https://img.shields.io/badge/rules-1,262-brightgreen)]()
[![Blog](https://img.shields.io/badge/blog-blog.valqore.io-black)](https://blog.valqore.io)

---

Valqore is an infrastructure governance engine that scans Kubernetes manifests, Terraform configurations, and cloud resources — then returns a **score (0-100)** and a **verdict** (PASS, PASS_WITH_MONITORING, or BLOCK).

1,262 built-in rules across security, cost, carbon, compliance, and AI governance. No configuration needed.

## What You Get

- **Valqore Score** — composite 0-100 score with sub-scores for Security, Reliability, Cost, Carbon, and Compliance
- **Cost estimation** — $/month estimates across AWS, Azure, and GCP with right-sizing recommendations
- **Carbon tracking** — CO2e per workload, greener region suggestions, 77 regions supported
- **Drift detection** — compare Terraform state against live cloud resources, attribute changes via CloudTrail
- **AI governance** — detect ungoverned AI/ML workloads, enforce EU AI Act compliance, gate model promotions
- **Compliance evidence** — audit-ready reports for HIPAA, SOC 2, PCI-DSS, GDPR, ISO 42001, and 7 more frameworks
- **FinOps** — cloud billing analysis, cost anomaly detection, budget gates for CI/CD
- **Container image audit** — detect outdated images, unpinned tags, registry violations
- **AI-powered explanations** — optional embedded AI model explains findings (fully offline, no API calls)

## Quick Start

```bash
docker pull valqore/engine:1.0.0

docker volume create valqore-data

docker run --rm -v valqore-data:/home/valqore/.valqore \
  valqore/engine:1.0.0 activate YOUR_LICENSE_KEY

docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evaluate /workspace/deploy.yaml --score
```

**Output:**

```
Valqore Score: 84/100 (Grade: B)
  Security: 78 | Reliability: 77 | Cost: 90 | Carbon: 97 | Compliance: 100
Cost estimate: $19.53/mo (aws, us-east-1)

Verdict: BLOCK

Total: 495 | Pass: 383 | Warn: 84 | Fail: 28
```

Two image variants:
- `valqore/engine:1.0.0` — standard (626 MB)
- `valqore/engine:1.0.0-ai` — with embedded fine-tuned AI model for offline explanations (2.5 GB)

## Examples

Clone the repo and scan any folder. Each scenario contains realistic infrastructure with intentional misconfigurations for Valqore to catch.

```bash
git clone https://github.com/valqore/public.git
cd public

# Scan any example
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

#### E-Commerce Platform (`examples/ecommerce/`)
Storefront + cart + payment gateway + database. Common mistakes: hardcoded Stripe keys in env vars, payment service running privileged, database on emptyDir, public RDS, open security group.

#### SaaS Multi-Tenant Backend (`examples/saas-platform/`)
API gateway + auth + tenant service + workers. Common mistakes: JWT secrets in plain text, unpinned images, no network segmentation between tenants.

#### Data Pipeline (`examples/data-pipeline/`)
Kafka + Spark + Elasticsearch + ETL cron job. Common mistakes: AWS credentials hardcoded in env, Spark running as root, Elasticsearch privileged, stateful data on emptyDir.

#### Startup MVP (`examples/startup-mvp/`)
Single-pod Node.js app with MongoDB sidecar. Common mistakes: MongoDB connection string with password in env, database on emptyDir, default namespace, NodePort exposure.

#### Fintech Trading Platform (`examples/fintech/`)
Order matching engine + market data feed + risk calculator with GPU. Common mistakes: privileged trading engine, API keys in env, public database, no encryption, single-AZ database for a trading system.

#### Azure Web App (`examples/azure/`)
App Service + SQL Server + Storage Account. Common mistakes: TLS 1.0, FTPS allowed, public SQL server, storage with public access, secrets in app settings.

#### GCP GKE Cluster (`examples/gcp/`)
GKE cluster + Cloud SQL + Storage + Firewall. Common mistakes: legacy ABAC enabled, overly broad OAuth scopes, public Cloud SQL, firewall allowing all inbound.

---

## Use Cases

### Block insecure PRs in CI/CD

Run Valqore as a GitHub Actions step. If the verdict is BLOCK, the PR fails — before anything reaches production.

```
Valqore Score: 55/100 (Grade: D)
Verdict: BLOCK
BLOCKED: 42 failure(s). 3 CRITICAL finding(s) must be fixed.
```

### Catch cost waste before it ships

A single `evaluate --score` shows the estimated monthly cost. Spot over-provisioned resources, missing Graviton migrations, and untagged workloads that can't be attributed to any team.

```
Cost estimate: $847/mo (aws, us-east-1)
What-if Graviton: $677/mo (-20%, -69% carbon)
What-if Spot 70%: $491/mo (-42%)
```

### Monitor cloud billing with budget gates

Set a cost threshold in your pipeline. If monthly spend exceeds it, the build fails.

```bash
valqore finops billing --cloud aws --fail-if-over 5000
# COST GATE FAILED: $5,231/month exceeds threshold $5,000
```

### Detect infrastructure drift

Compare Terraform state against live AWS/Azure resources. See what changed, when, and who changed it (via CloudTrail).

```
Drift detected: 3 resources changed
  aws_security_group.web: ingress rule added (port 22, 0.0.0.0/0)
    Changed by: arn:aws:iam::123:user/developer@company.com
    Changed at: 2026-04-14 15:32:00
```

### Gate AI workloads before production

Block ungoverned AI/ML deployments. Require EU AI Act risk classification, human oversight, kill switch, and model versioning before any GPU workload reaches production.

```
=== AI Promotion Gates: ml-inference -> production ===
  AI Registered:            FAIL
  Human Oversight:          FAIL
  EU AI Act Classification: FAIL
  Kill Switch:              FAIL
  Result: BLOCKED -- 4 of 5 gates failing
```

### Generate compliance evidence

One command produces audit-ready compliance reports mapped to regulatory controls.

```bash
valqore evidence hipaa -f /workspace/kubernetes/
# Compliance rate: 85.7% | Controls: 7 | Passing: 6 | Failing: 1
```

Available packs: `hipaa`, `soc2`, `pci_dss`, `gdpr`, `eu_ai_act`, `nist_ai_rmf`, `iso_42001`, and 5 more.

---

## CI/CD Integration

```yaml
# GitHub Actions
- name: Valqore Gate
  run: |
    docker run --rm \
      -v ${{ github.workspace }}:/workspace \
      -v valqore-data:/home/valqore/.valqore \
      valqore/engine:1.0.0 evaluate /workspace/ --score --fail-on block
```

Exit code 1 on BLOCK = PR fails.

## Multi-Cloud

Works with **AWS, Azure, GCP**, and any Kubernetes cluster. Read-only by design — Valqore never creates, modifies, or deletes your resources.

## Blog

Technical deep-dives and real-world examples:
- [blog/](blog/) — code examples and training data from published posts
- [blog.valqore.io](https://blog.valqore.io) — full articles

## Links

- Website: [valqore.io](https://www.valqore.io)
- Docker Hub: [valqore/engine](https://hub.docker.com/r/valqore/engine)
- Blog: [blog.valqore.io](https://blog.valqore.io)
- Book a demo: [calendly.com/tuncvalqore](https://calendly.com/tuncvalqore/30min)
- Email: tunc@valqore.io

---

VALQORE is a pending trademark. All rights reserved. See [LICENSE](LICENSE).
