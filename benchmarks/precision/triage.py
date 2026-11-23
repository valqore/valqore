"""Bucket findings by systemic cause.

The buckets are decided by the finding's own message, not by my opinion of the
rule, so the counts can be re-derived by anyone with the JSON. Every bucket but
REAL is a candidate false positive for a STATIC scan of a repository; REAL is
everything the rule could actually know from the file in front of it.
"""
import json
import re
import sys
from collections import Counter, defaultdict

BUCKETS = [
    # (name, why it is not a finding, matcher on the message)
    ("ENGINE-ERROR", "the rule raised an exception and the exception was reported as a finding",
     re.compile(r"^Rule evaluation error", re.I)),
    ("NO-DATA", "needs live telemetry the static scan never had",
     re.compile(r"\bno .{0,40}data (is )?available|not assessed|data unavailable|"
                r"has never been used or last_used_date is unavailable", re.I)),
    ("DECLARE", "demands a valqore.io/* or governance annotation declaring a fact about the organisation",
     re.compile(r"not declared|does not have an? .{0,40}(annotation|label)|"
                r"no .{0,40}annotation (found|declared)|not identified|not documented", re.I)),
]


def bucket(msg: str) -> str:
    for name, _why, rx in BUCKETS:
        if rx.search(msg):
            return name
    return "REAL"


def main(path: str, label: str) -> None:
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    findings = [r for r in d["results"]
                if r["outcome"] not in ("PASS", "SKIP", "NOT_APPLICABLE")]

    counts = Counter()
    rules_in = defaultdict(set)
    for r in findings:
        b = bucket(r["message"])
        counts[b] += 1
        rules_in[b].add(r["rule_id"])

    total = len(findings)
    print("=" * 70)
    print(label, "-", total, "findings")
    for name, why, _rx in BUCKETS + [("REAL", "the rule could know this from the file", None)]:
        n = counts[name]
        pct = (100.0 * n / total) if total else 0
        print(f"  {name:<13} {n:5d}  {pct:5.1f}%   ({len(rules_in[name])} rules)  {why}")

    # duplication: how many distinct resources, and the worst repeated message
    per_msg = Counter(r["message"][:60] for r in findings)
    print("\n  most repeated single message:", per_msg.most_common(1)[0])
    print("  distinct resources:", len({r["resource_id"] for r in d["results"]}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
