# Blog Post #4 — AI Governance on AKS

Example files for the blog post "The $47,000 AI Agent Bill — And Why August 2026 Changes Everything."

Try them yourself.

## Prerequisites

```bash
docker pull valqore/engine:1.0.0
docker volume create valqore-data

docker run --rm -v valqore-data:/home/valqore/.valqore \
  valqore/engine:1.0.0 activate YOUR_LICENSE_KEY
```

## Try It

### 1. Scan the ungoverned LLM deployment — 5 of 5 gates fail

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 ai-gate /workspace/azure-llm-inference-ungoverned.yaml
```

Expected: BLOCKED, 5 of 5 gates failing.

### 2. Scan the governed version — all 5 gates pass

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 ai-gate /workspace/azure-llm-inference-governed.yaml
```

Expected: PASSED, all 5 gates cleared, Score 87/100.

### 3. Full evaluation with AI governance findings

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evaluate /workspace/azure-llm-inference-ungoverned.yaml --score
```

### 4. Generate EU AI Act compliance evidence

```bash
docker run --rm \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0 evidence eu_ai_act -f /workspace/
```

### 5. Chat: ask questions in plain English

```bash
docker run --rm -it \
  -v valqore-data:/home/valqore/.valqore \
  -v $(pwd):/workspace \
  valqore/engine:1.0.0-ai chat --dir /workspace

# Try asking:
#   "Are we EU AI Act compliant?"
#   "What AI workloads are running?"
#   "How do we fix the agent?"
```

## Files

- `azure-llm-inference-ungoverned.yaml` — vLLM + LangChain agent, no governance (will fail all gates)
- `azure-llm-inference-governed.yaml` — same workload with proper annotations (passes all gates)

## What the gates check

| Gate | Requirement |
|------|-------------|
| AI Registered | `valqore.io/ai-registered=true` annotation |
| Human Oversight | `valqore.io/human-oversight` documented |
| EU AI Act Classification | `valqore.io/ai-risk-level` set (minimal/limited/high/unacceptable) |
| Kill Switch | `valqore.io/kill-switch=enabled` |
| AIG Score | Minimum 70/100 across 128 AI governance rules |
