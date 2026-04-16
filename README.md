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

Try scanning these with Valqore:

| File | What It Tests |
|------|--------------|
| [examples/insecure-deploy.yaml](examples/insecure-deploy.yaml) | Privileged container, unpinned image, no NetworkPolicy |
| [examples/insecure-terraform.tf](examples/insecure-terraform.tf) | Public RDS, open security group, unencrypted S3 |
| [examples/ai-workload.yaml](examples/ai-workload.yaml) | Ungoverned GPU workload, missing AI governance annotations |

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
