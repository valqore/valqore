# Blog Post #6 — Learn Normal, Flag New

Example files for the blog post **"Learn Normal, Flag New — For What Agents
Actually Change."** Rules catch known-bad. This shows the other half: mine a
config-template *shape* from every resource, learn what an environment's normal
looks like, and flag a genuinely new shape — even when no rule fired.

Try it on the **free, tokenless public image** — no key, no signup:

```bash
docker pull ghcr.io/valqore/engine:1.12.1
```

The catalog of "what's normal" persists on disk, so use a named volume across
runs (and set the promotion threshold to 1 so a single sighting counts as
learned — the default is 5):

```bash
docker volume create valqore-catalog
```

## Try It

### 1. Learn your normal (training mode — observe only, surface nothing)

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -v valqore-catalog:/home/valqore/.valqore \
  -e VALQORE_PATTERN_PROMOTION_THRESHOLD=1 \
  ghcr.io/valqore/engine:1.12.1 \
  valqore novelty /workspace/inventory-baseline.json --mode training
```

The engine records the shapes of your normal inventory — three web Deployments
and an IAM read role. Nothing is surfaced; it's learning.

### 2. Scan a new inventory (detect mode) — only the genuinely new shape is flagged

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -v valqore-catalog:/home/valqore/.valqore \
  ghcr.io/valqore/engine:1.12.1 \
  valqore novelty /workspace/inventory-new.json --mode detect
```

Expected: **one NOVEL finding — `prod/rogue-agent`**. The new Deployment and IAM
role match learned shapes and pass silently; the privileged, host-access pod is a
shape this environment has never produced, so it's flagged — even though you
never wrote a rule for it.

```
Novelty assessment (detect) -- 3 resource(s), 1 novel/spike
┌─────────┬──────┬──────────────────┬──────────────┐
│ Verdict │ Kind │ Resource         │ Reason       │
├─────────┼──────┼──────────────────┼──────────────┤
│ novel   │ Pod  │ prod/rogue-agent │ unseen shape │
└─────────┴──────┴──────────────────┴──────────────┘
```

### 3. The catalog + the shadow-review learning loop

```bash
# what shapes has this environment learned?
docker run --rm -v valqore-catalog:/home/valqore/.valqore \
  ghcr.io/valqore/engine:1.12.1 valqore patterns

# blocked action patterns awaiting a human "known-good" label (the shadow loop)
docker run --rm -v valqore-catalog:/home/valqore/.valqore \
  ghcr.io/valqore/engine:1.12.1 valqore agent-gate shadow
```

Mark a noisy false-block known-good once, and its future blocks are suppressed
while the rule's verdict stays honest in the evidence — the false-positive rate
becomes a learning loop that drives itself down. High-blast patterns can never be
suppressed.

## Files

- `inventory-baseline.json` — the org's "normal": three same-shaped web Deployments + an IAM read role.
- `inventory-new.json` — a later scan: new-but-known-shaped resources + one genuinely new shape (`prod/rogue-agent`, a privileged host-access pod).

## Training → Shadow → Detect

You never flip a "flag new" system from off to blocking in one step. The three
modes are the adoption ladder:

| Mode | Behavior |
|------|----------|
| `training` | record shapes only — learn what's normal |
| `shadow` | classify + mark "would surface" — dry-run confidence |
| `detect` | surface NOVEL / SPIKE findings — live |

This **extends** the 1,379-rule engine; it never replaces it. Rules stay the
deterministic source of truth and the artifact you show an auditor — novelty is
the tripwire for the unknown-unknowns.
