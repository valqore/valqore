#!/usr/bin/env python3
"""Gate a runbook-reading incident agent with Valqore.

Tools like Versus Incident's `find_runbook` (https://github.com/versuscontrol/versus-incident)
use RAG to surface the *right* runbook during an incident -- read-only, "a human
still decides." That posture is exactly right, and it's one wire away from danger:
the runbook this demo retrieves literally ends with "roll back the api deploy."
The moment an agent can act on what it reads, the recommendation becomes an
action -- and that action needs a deterministic gate.

Valqore is that gate. This script drives the REAL `valqore mcp-gate` over the
policy in this directory to show the split:

  - the read-only `incident-responder` may retrieve the runbook and run the
    read-only diagnostic query, but is BLOCKED from the destructive steps the
    runbook recommends (out of its tool scope);
  - a privileged `remediation-agent` may attempt the rollback, but it's held for
    a signed human approval -- "a human still decides," enforced, with evidence.

Run:  python examples/versus_incident_gate/demo.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
POL = str(HERE / "mcp-policy.json")
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def check(title, tool, *, agent=None, approved=False, expect_allow):
    args = ["mcp-gate", "check", tool, "--policy", POL]
    if agent:
        args += ["--agent", agent]
    if approved:
        args += ["--approved"]
    print("\n" + "=" * 78)
    print(f"# {title}")
    print(f"$ valqore {' '.join(args)}")
    print("-" * 78)
    proc = subprocess.run([sys.executable, "-m", "valqore.cli.main", *args],
                          cwd=ROOT, env=ENV, capture_output=True, text=True)
    print(((proc.stdout or "") + (proc.stderr or "")).rstrip())
    allowed = proc.returncode == 0
    ok = "OK" if allowed == expect_allow else "UNEXPECTED"
    if ok == "UNEXPECTED":
        _FAILURES.append(f"{title} -> got {'ALLOW' if allowed else 'BLOCK'}")
    print(f"-- exit {proc.returncode} [{'ALLOW' if allowed else 'BLOCK'} / expected "
          f"{'ALLOW' if expect_allow else 'BLOCK'}: {ok}]")


_FAILURES: list[str] = []


def main():
    print("Runbook the agent retrieves:", HERE / "runbook.md")

    print("\n" + "#" * 78)
    print("# A. Read-only incident-responder (the Versus Incident posture)")
    check("retrieve the runbook -- read-only, in scope", "find_runbook",
          agent="incident-responder", expect_allow=True)
    check("run the read-only diagnostic query (runbook step 1)", "pg_query",
          agent="incident-responder", expect_allow=True)
    check("runbook step 2 'terminate idle-in-transaction' -- a WRITE, out of scope",
          "pg_terminate_backend", agent="incident-responder", expect_allow=False)
    check("runbook step 3 'roll back the api deploy' -- out of scope + destructive",
          "argo_rollback", agent="incident-responder", expect_allow=False)

    print("\n" + "#" * 78)
    print("# B. Privileged remediation-agent -- a human still decides")
    check("rollback is in scope, but high blast -> held for signed approval",
          "argo_rollback", agent="remediation-agent", expect_allow=False)
    check("...with a valid signed approval, it executes", "argo_rollback",
          agent="remediation-agent", approved=True, expect_allow=True)

    print("\n" + "=" * 78)
    print("Versus Incident finds the right runbook. Valqore decides whether the agent")
    print("may execute what the runbook recommends -- deterministically, with a signed")
    print("journal. `valqore mcp-gate journal` shows every decision.")

    if _FAILURES:
        print("\nFAILED checks (regression):")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
