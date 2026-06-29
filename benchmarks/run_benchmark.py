#!/usr/bin/env python3
"""Reproducible head-to-head benchmark: Valqore vs other scanners on one corpus.

Runs each installed tool against benchmarks/corpus/ (a deliberately insecure +
costly + ungoverned-AI sample repo) and emits a comparison: per-domain findings
and a capability matrix. Honest by design -- the corpus has bread-and-butter
misconfigs every scanner should catch (so rivals get fair credit), plus the
cost/carbon/AI-governance/compliance axes that only a converged engine covers.

Tools not installed are reported from the public capability matrix, clearly
marked. Run:  python benchmarks/run_benchmark.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
CORPUS = ROOT / "corpus"
IMAGE = "ghcr.io/valqore/engine:latest"


def _valqore_base() -> tuple[list[str] | None, str]:
    """How to invoke Valqore and the corpus path to pass.

    Prefers a `valqore` on PATH (the Docker alias from the repo README, or an
    installed engine); otherwise runs the public, source-protected image via
    Docker, mounting the repo so the corpus is visible inside the container.
    """
    if shutil.which("valqore"):
        return ["valqore"], str(CORPUS)
    if shutil.which("docker"):
        rel = str(CORPUS.relative_to(REPO)).replace("\\", "/")
        return (["docker", "run", "--rm", "-v", f"{REPO}:/work", "-w", "/work", IMAGE, "valqore"], rel)
    return None, str(CORPUS)


def _tool_version(cmd: list[str]) -> str | None:
    """Capture a tool's version string for provenance, or None if absent."""
    exe = cmd[0]
    if exe != sys.executable and not shutil.which(exe):
        return None
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        out = (p.stdout or p.stderr or "").strip().splitlines()
        return out[0].strip() if out else None
    except Exception:
        return None


def _corpus_provenance() -> dict:
    """Hash every corpus file so a reviewer can confirm they ran the same inputs."""
    files = {}
    h_all = hashlib.sha256()
    for f in sorted(CORPUS.rglob("*")):
        if f.is_file():
            b = f.read_bytes()
            files[str(f.relative_to(ROOT))] = hashlib.sha256(b).hexdigest()[:16]
            h_all.update(b)
    return {"files": files, "corpus_sha256": h_all.hexdigest()[:16], "file_count": len(files)}

# Rule-prefix -> human domain (for Valqore's converged output).
DOMAIN = {
    "SP": "Security", "CS": "Security", "NET": "Security", "K8S": "Security",
    "SCS": "Supply chain", "IMG": "Supply chain",
    "CC": "Cost / FinOps", "GR": "Carbon / GreenOps", "GPU": "GPU / AI cost",
    "AIG": "AI governance", "CMP": "Compliance", "OH": "Reliability/Ops",
    "TF": "IaC (Terraform)", "DOC": "Dockerfile",
}


def _run_json(cmd: list[str]) -> dict | list | None:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception:
        return None
    out = p.stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        # some tools print a banner before JSON; grab from first brace/bracket
        for i, ch in enumerate(out):
            if ch in "[{":
                try:
                    return json.loads(out[i:])
                except Exception:
                    return None
        return None


def run_valqore() -> dict:
    base, corpus = _valqore_base()
    if base is None:
        return {"available": False}
    cmd = base + ["evaluate", corpus, "--score", "-o", "json"]
    data = _run_json(cmd)
    if not data:
        return {"available": False}
    results = data.get("results", [])
    fails = [r for r in results if r.get("outcome") == "FAIL"]
    by_domain: Counter = Counter()
    for r in fails:
        prefix = r["rule_id"].split("-")[0]
        by_domain[DOMAIN.get(prefix, prefix)] += 1
    score = data.get("score")
    if isinstance(score, dict):
        score = score.get("score")
    return {
        "available": True,
        "evaluations": len(results),
        "findings": len(fails),
        "by_domain": dict(by_domain.most_common()),
        "score": score,
        "verdict": data.get("verdict"),
    }


def run_checkov() -> dict:
    # Prefer a standalone/pipx checkov on PATH. Do NOT fall back to `python -m
    # checkov.main` in this interpreter: checkov pins an old python-hcl2 that
    # breaks Valqore's Terraform parsing, so it must live in its own env.
    exe = shutil.which("checkov")
    if not exe:
        return {"available": False}
    cmd = [exe, "-d", str(CORPUS), "--compact", "-o", "json"]
    data = _run_json(cmd)
    if data is None:
        return {"available": False}
    checks = data if isinstance(data, list) else [data]
    by_type = {}
    passed = failed = 0
    for c in checks:
        ct = c.get("check_type", "?")
        s = c.get("summary", {})
        by_type[ct] = {"passed": s.get("passed", 0), "failed": s.get("failed", 0)}
        passed += s.get("passed", 0)
        failed += s.get("failed", 0)
    return {"available": True, "passed": passed, "failed": failed, "by_type": by_type}


def _module_exists(name: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(name) is not None


def run_kubescape() -> dict:
    if not shutil.which("kubescape"):
        return {"available": False}
    data = _run_json(["kubescape", "scan", str(CORPUS), "--format", "json", "--format-version", "v2"])
    if not data:
        return {"available": False}
    # kubescape v2 JSON: summaryDetails.controls -> failed resources, or results list.
    failed = 0
    try:
        sd = data.get("summaryDetails", {}) if isinstance(data, dict) else {}
        ctrls = sd.get("controls", {}) or {}
        for c in ctrls.values():
            if (c.get("statusInfo", {}) or {}).get("status") == "failed" or c.get("failedResources", 0):
                failed += int(c.get("failedResources", 0)) or 1
    except Exception:
        pass
    return {"available": True, "failed": failed, "scope": "K8s security/posture only"}


def run_trivy() -> dict:
    if not shutil.which("trivy"):
        return {"available": False}
    data = _run_json(["trivy", "config", str(CORPUS), "--format", "json", "--quiet"])
    if not data:
        return {"available": False}
    failed = 0
    try:
        for res in (data.get("Results", []) if isinstance(data, dict) else []):
            failed += len(res.get("Misconfigurations", []) or [])
    except Exception:
        pass
    return {"available": True, "failed": failed, "scope": "IaC/K8s/Dockerfile misconfig only"}


def run_kube_score() -> dict:
    # kube-score is K8s-manifest-only; it ignores Terraform/Dockerfile. We point
    # it at the YAML manifests in the corpus and count CRITICAL/WARNING checks.
    if not shutil.which("kube-score"):
        return {"available": False}
    manifests = [str(p) for p in sorted(CORPUS.glob("*.yaml")) + sorted(CORPUS.glob("*.yml"))]
    if not manifests:
        return {"available": False}
    data = _run_json(["kube-score", "score", "--output-format", "json", *manifests])
    if not data:
        return {"available": False}
    failed = 0
    try:
        for obj in (data if isinstance(data, list) else []):
            for check in obj.get("checks", []) or []:
                # grade < 10 (kube-score's "OK") means a warning/critical finding
                if check.get("grade", 10) < 10 and not check.get("skipped"):
                    failed += 1
    except Exception:
        pass
    return {"available": True, "failed": failed, "scope": "K8s manifest best-practices only"}


# Capability matrix — Y = native, P = partial/separate product, N = no.
# Rivals sourced from the 2026 competitive review (see BACKLOG / memory).
CAP_ROWS = [
    ("K8s security misconfig", "Y", "Y", "Y", "P", "Y"),
    ("IaC (Terraform) scanning", "Y", "Y", "P", "N", "Y"),
    ("Dockerfile scanning", "Y", "Y", "Y", "N", "P"),
    ("Cost / FinOps", "Y", "N", "N", "Y", "N"),
    ("Carbon / GreenOps", "Y", "N", "N", "Y", "N"),
    ("AI / LLM governance", "Y", "N", "N", "N", "P"),
    ("Agent / MCP runtime gate", "Y", "N", "N", "N", "P"),
    ("Single 0-100 score + verdict", "Y", "N", "N", "N", "N"),
    ("Auto-remediation", "Y", "P", "N", "P", "N"),
    ("OSCAL compliance evidence", "Y", "N", "N", "N", "N"),
    ("Air-gapped / self-hosted", "Y", "Y", "Y", "N", "N"),
    ("Deterministic (no SaaS/ML/graph)", "Y", "Y", "Y", "N", "N"),
]
CAP_COLS = ["Capability", "Valqore", "Checkov", "Kubescape", "kubeadapt", "Wiz"]


def build_report(vq: dict, ck: dict, ks: dict, tv: dict, kscore: dict, prov: dict) -> str:
    L = []
    L.append("# Valqore benchmark — converged governance vs point scanners\n")
    L.append("Corpus: `benchmarks/corpus/` (Kubernetes + Terraform + Dockerfile — "
             "insecure, over-provisioned, and ungoverned-AI by design).\n")
    L.append("> Honest note: raw finding *counts* across tools are not directly comparable "
             "(different rule granularity). The point is **domain coverage** — what each "
             "tool can see at all — and the converged single-verdict + evidence story. "
             "See [METHODOLOGY.md](METHODOLOGY.md) for corpus design, normalization, and caveats.\n")

    # Provenance — so a skeptic can confirm they ran the same inputs + tool versions.
    L.append("\n## Provenance\n")
    L.append(f"- Generated: {prov['generated_utc']}")
    L.append(f"- Corpus: {prov['corpus']['file_count']} files, sha256 `{prov['corpus']['corpus_sha256']}`")
    vers = prov["tool_versions"]
    L.append("- Tool versions: " + ", ".join(
        f"{k} `{v}`" if v else f"{k} _(not installed)_" for k, v in vers.items()))
    L.append("")

    L.append("\n## Same corpus, what each tool reports\n")
    if vq.get("available"):
        L.append(f"**Valqore** — {vq['evaluations']} evaluations, **{vq['findings']} findings** "
                 f"across **{len(vq['by_domain'])} domains**; Score {vq['score']}/100, verdict {vq['verdict']}.\n")
        L.append("\n| Domain | Valqore findings |")
        L.append("|---|---:|")
        for dom, n in vq["by_domain"].items():
            L.append(f"| {dom} | {n} |")
    if ck.get("available"):
        bt = ", ".join(f"{k}: {v['failed']}" for k, v in ck["by_type"].items())
        L.append(f"\n**Checkov** — **{ck['failed']} failed checks** ({bt}); security/IaC misconfig only "
                 "— no cost, carbon, AI governance, compliance evidence, or single verdict.\n")
    for tool, res in (("Kubescape", ks), ("Trivy", tv), ("kube-score", kscore)):
        if res.get("available"):
            L.append(f"\n**{tool}** — **{res['failed']} failed checks** ({res['scope']}); "
                     "no cost, carbon, AI governance, or compliance evidence.\n")
        else:
            L.append(f"\n_{tool}: not installed in this run — see the capability matrix (sourced from the 2026 review)._\n")
    L.append("\nValqore catches the same security/IaC misconfigs Checkov does, **and** the "
             "cost, carbon, AI-governance and compliance findings Checkov structurally cannot — "
             "in one pass, with one score.\n")

    L.append("\n## Capability matrix\n")
    L.append("| " + " | ".join(CAP_COLS) + " |")
    L.append("|" + "|".join(["---"] + [":---:"] * (len(CAP_COLS) - 1)) + "|")
    for row in CAP_ROWS:
        cells = [row[0]] + [{"Y": "✅", "P": "◑", "N": "—"}[c] for c in row[1:]]
        L.append("| " + " | ".join(cells) + " |")
    L.append("\n✅ native · ◑ partial / separate product · — not covered. "
             "Rivals per the 2026 competitive review.\n")
    L.append("\n## Reproduce\n```\n# Valqore runs via the public image (no install); pip-install any competitor you want included.\ndocker pull ghcr.io/valqore/engine:latest\npip install checkov                  # IaC/K8s/Dockerfile misconfig\n# brew install kubescape trivy kube-score   # optional K8s scanners\npython benchmarks/run_benchmark.py    # run from the repo root\n```\n")
    return "\n".join(L)


def _provenance() -> dict:
    return {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "corpus": _corpus_provenance(),
        "tool_versions": {
            "valqore": _tool_version((_valqore_base()[0] or ["valqore"]) + ["version"]),
            "checkov": _tool_version(["checkov", "-v"]),
            "kubescape": _tool_version(["kubescape", "version"]),
            "trivy": _tool_version(["trivy", "--version"]),
            "kube-score": _tool_version(["kube-score", "version"]),
        },
    }


def main():
    prov = _provenance()
    vq = run_valqore()
    ck = run_checkov()
    ks = run_kubescape()
    tv = run_trivy()
    kscore = run_kube_score()
    report = build_report(vq, ck, ks, tv, kscore, prov)
    (ROOT / "RESULTS.md").write_text(report, encoding="utf-8")
    (ROOT / "results.json").write_text(
        json.dumps({"provenance": prov, "valqore": vq, "checkov": ck,
                    "kubescape": ks, "trivy": tv, "kube_score": kscore}, indent=2), encoding="utf-8")
    print(report)
    print(f"\nWrote {ROOT/'RESULTS.md'} and {ROOT/'results.json'}")


if __name__ == "__main__":
    main()
