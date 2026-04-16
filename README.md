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

Try scanning these with Valqore — compare insecure vs secure versions to see the score difference:

### Kubernetes

| File | Score | What It Tests |
|------|-------|--------------|
| [insecure-deploy.yaml](examples/insecure-deploy.yaml) | ~84 (B) | Privileged container, unpinned image, no NetworkPolicy |
| [secure-deploy.yaml](examples/secure-deploy.yaml) | ~97 (A) | Hardened security context, NetworkPolicy, topology spread |
| [microservices-stack.yaml](examples/microservices-stack.yaml) | ~55 (D) | Hardcoded secrets, no resource limits, privileged containers |
| [ai-workload.yaml](examples/ai-workload.yaml) | AI gate: BLOCK | Ungoverned GPU workload, missing AI governance annotations |
| [gpu-ml-training.yaml](examples/gpu-ml-training.yaml) | AI gate: PASS | Proper AI annotations, kill switch, human oversight |

### Terraform

| File | Score | What It Tests |
|------|-------|--------------|
| [insecure-terraform.tf](examples/insecure-terraform.tf) | ~71 (C) | Public RDS, open security group, unencrypted S3, no state locking |
| [secure-terraform.tf](examples/secure-terraform.tf) | ~95 (A) | Encrypted storage, private subnets, Graviton instances, DynamoDB locking |

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
