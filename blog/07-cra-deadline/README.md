# Blog Post #7 — The CRA 24-Hour Clock

Example files for the blog post **"The 24-Hour Clock: Can You File a CRA Report
by September 11?"** On **11 September 2026** the EU Cyber Resilience Act's
Article 14 reporting duties go live — an actively-exploited vulnerability must be
reported to ENISA within **24 hours**, a fuller notification within 72, a final
report within 14 days. A 24-hour clock is only meetable if the prerequisites
already exist. This shows how to check, deterministically, whether they do.

Try it on the **free, tokenless public image** — no key, no signup:

```bash
docker pull ghcr.io/valqore/engine:1.12.1
```

## Try It

### 1. Can you even file the early warning in time?

```bash
docker run --rm -v "$(pwd):/work" -w /work ghcr.io/valqore/engine:1.12.1 \
  valqore cra-report /work/product-deployment.yaml
```

Expected — the uncomfortable truth, up front:

```
CRA Art.14 reporting readiness — 0%
CRA Art.14 NOT ready: 4 prerequisite(s) missing (security_contact, cvd_policy,
manufacturer_id, sbom) — cannot meet the 24h notification clock.
Clock: 24h early warning · 72h notification · 14d final report
```

…followed by the **Article 14 report skeleton** — the exact JSON you'd file,
pre-populated with the deadline and the recipients (ENISA + your national CSIRT).
The empty fields are your gap list. Close them now, not on hour 23.

### 2. Generate the report skeleton for a given stage

```bash
docker run --rm -v "$(pwd):/work" -w /work ghcr.io/valqore/engine:1.12.1 \
  valqore cra-report /work/product-deployment.yaml --stage notification -o /work/art14-report.json
```

`--stage` is `early-warning` (24h) · `notification` (72h) · `final` (14d).

### 3. The Annex I conformity evidence — machine-readable, not a slide

```bash
docker run --rm -v "$(pwd):/work" -w /work ghcr.io/valqore/engine:1.12.1 \
  valqore evidence cra -f /work/product-deployment.yaml
```

Expected: `Deterministic evaluation of 10 controls. Verdict: BLOCK.` — NIST OSCAL
1.1.2 output an assessor or a customer's procurement team ingests directly. SBOM
presence, secure-by-default config, update mechanism, and vulnerability-handling
each get a PASS/FAIL.

## Files

- `product-deployment.yaml` — a "product with digital elements" as most teams ship it: no security contact, CVD policy, manufacturer id, or SBOM reference (all four are Article 14 prerequisites).

## The four prerequisites the 24h clock needs

| To report in 24h you need… | …which requires (already in place) |
|---|---|
| the affected **versions** | an **SBOM** — you can't scope what you can't inventory |
| a credible **early warning** | a **security contact** ENISA can reach |
| an intake path | a **coordinated vulnerability disclosure (CVD) policy** |
| attribution | a **manufacturer identity** on the product |

Run the check in CI now, close the four, and turn "can we even file in time?"
into a deterministic, evidenced *yes* — the same engine, from a file, a live
cluster, or a live cloud account.
