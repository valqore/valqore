#!/usr/bin/env python3
"""Govern kagent agents with Valqore -- end-to-end proof (Theme P).

kagent (CNCF / Solo.io) is a fast-growing agentic framework: you `kubectl apply`
an `Agent` CRD and it runs, delegates (A2A), and calls tools over MCP. It enforces
no deterministic policy and emits no compliance evidence. Valqore is the
independent governance + enforcement layer over it.

This script drives the REAL `valqore` CLI (no mocks) over the manifests in this
directory to show, in order:

  1. P-1/P-4/P-6  Discover + audit an UNGOVERNED kagent fleet with zero opt-in:
                  native Agent-CRD detection, a delegation cycle, a shadow
                  (unlabeled BYO LangGraph) agent.
  2. P-5          Ground the audit in observed telemetry -- the troubleshooter
                  ran 1,500 steps with no cap (HIGH unbounded at runtime).
  3. P-1/P-7      The SAME agent brought to GOVERNED, verified cross-resource
                  against a real dedicated SA + default-deny egress NetworkPolicy.
  4. P-3          Gate kagent's live MCP tool calls deterministically, per agent.
  5. P-2          Compile the agent rules to a native Kubernetes
                  ValidatingAdmissionPolicy that gates `kagent.dev/agents` at
                  admission -- Valqore out of the data path.

Run:  python examples/kagent_governance/demo.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


_FAILURES: list[str] = []


def run(title: str, args: list[str], *, expect_fail: bool = False) -> None:
    print("\n" + "=" * 78)
    print(f"# {title}")
    print(f"$ valqore {' '.join(args)}")
    print("-" * 78)
    proc = subprocess.run([sys.executable, "-m", "valqore.cli.main", *args],
                          cwd=ROOT, env=ENV, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.rstrip())
    verdict = "BLOCK/FAIL (expected)" if expect_fail else "OK"
    if (proc.returncode != 0) != expect_fail:
        verdict = f"UNEXPECTED exit {proc.returncode}"
        _FAILURES.append(f"{title} -> {verdict}")
    print(f"-- exit {proc.returncode} [{verdict}]")


def main() -> None:
    ung = str(HERE / "agents-ungoverned.yaml")
    gov = str(HERE / "agents-governed.yaml")
    tel = str(HERE / "telemetry.prom")
    pol = str(HERE / "mcp-policy.json")

    run("1+2. Audit the UNGOVERNED kagent fleet, grounded in runtime telemetry",
        ["agent-audit", ung, "--telemetry", tel])

    run("3. The SAME agent, GOVERNED -- verified against real SA + NetworkPolicy",
        ["agent-audit", gov])

    print("\n" + "#" * 78)
    print("# 4. Gate kagent's MCP tool calls deterministically, per agent (P-3)")
    run("troubleshooter is read-only scoped -> a delete is BLOCKED",
        ["mcp-gate", "check", "k8s_delete_resource", "--agent", "k8s-troubleshooter", "--policy", pol],
        expect_fail=True)
    run("an in-scope read is ALLOWED",
        ["mcp-gate", "check", "k8s_get_pods", "--agent", "k8s-troubleshooter", "--policy", pol])
    run("a destructive Helm verb is BLOCKED on blast radius alone",
        ["mcp-gate", "check", "helm_uninstall", "--policy", pol], expect_fail=True)

    run("5. Compile the agent rules to a native VAP gating kagent.dev/agents (P-2)",
        ["vap-export", "-r", "AIG-145,AIG-150", "--agent-crds"])

    print("\n" + "=" * 78)
    print("Done. Same engine, same rules as CI/CD, the webhook, and OSCAL export --")
    print("now over your kagent fleet. Add --format oscal -o evidence.json for auditors.")

    if _FAILURES:
        print("\nFAILED steps (regression):")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
