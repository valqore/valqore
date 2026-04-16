# Blog Post #3 — GreenOps: Your Cloud Has a Carbon Footprint

Example files and commands from the blog post. Try them yourself.

## Prerequisites

```bash
docker pull valqore/engine:1.0.0
docker volume create valqore-data

# Activate your license
docker run --rm -v valqore-data:/home/valqore/.valqore \
  valqore/engine:1.0.0 activate YOUR_LICENSE_KEY
```

## Try It

### 1. Scan the high-carbon deployment (10 GPU replicas, us-east-1)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evaluate /workspace/high-carbon-deployment.yaml --score
```

Expected output:
```
Valqore Score: 89/100 (Grade: B)
  Security: 88 | Reliability: 86 | Cost: 87 | Carbon: 97 | Compliance: 95
Cost estimate: $11,212.80/mo (aws, us-east-1)
Carbon: 109.430 kg CO₂e/mo (aws:us-east-1)
```

### 2. Scan the optimized low-carbon deployment

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evaluate /workspace/low-carbon-deployment.yaml --score
```

Expected output:
```
Valqore Score: 93/100 (Grade: A)
  Security: 98 | Reliability: 88 | Cost: 90 | Carbon: 97 | Compliance: 93
Cost estimate: $1,868.80/mo (aws, us-east-1)
Carbon: 18.238 kg CO₂e/mo (aws:us-east-1)
```

**Result: 83% less cost, 83% less carbon, higher score.**

### 3. What-if: Migrate to Graviton (ARM)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 what-if /workspace/high-carbon-deployment.yaml --graviton
```

Expected output:
```
Cost:    $10,512/mo -> $8,410/mo  (-20%)
Carbon:  172.12 kg  -> 52.50 kg   (-69.5%)
```

### 4. What-if: Spot instances (carbon doesn't change!)

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 what-if /workspace/high-carbon-deployment.yaml --spot-ratio 70
```

Spot saves money but carbon stays the same — 0.0% reduction. Spot is a pricing mechanism, not a sustainability mechanism.

## Files

- `high-carbon-deployment.yaml` — 10 GPU transcoder + 20 batch workers + 5 analytics, all in us-east-1
- `low-carbon-deployment.yaml` — Right-sized, eu-north-1, carbon budgets, fewer replicas
