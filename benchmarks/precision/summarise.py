"""Summarise a valqore evaluate --output json run: outcomes, findings by rule."""
import json
import sys
from collections import Counter, defaultdict

path = sys.argv[1]
label = sys.argv[2]
with open(path, encoding="utf-8") as fh:
    d = json.load(fh)

results = d["results"]
outcomes = Counter(r["outcome"] for r in results)
findings = [r for r in results if r["outcome"] not in ("PASS", "SKIP", "NOT_APPLICABLE")]

print("=" * 72)
print(label, "| verdict", d.get("verdict"), "| evaluations", len(results))
print("outcomes:", dict(outcomes))
print("findings:", len(findings))
print("resources:", len({r["resource_id"] for r in results}))

by_sev = Counter(r["severity"] for r in findings)
print("by severity:", dict(by_sev))

by_rule = defaultdict(list)
for r in findings:
    by_rule[(r["rule_id"], r["severity"])].append(r)

print("\ndistinct rules firing:", len(by_rule))
print("\n-- every rule that fired, most instances first --")
for (rid, sev), rows in sorted(by_rule.items(), key=lambda kv: -len(kv[1])):
    msg = rows[0]["message"]
    if len(msg) > 88:
        msg = msg[:85] + "..."
    print(f"{len(rows):4d}  {rid:<16} {sev:<9} {msg}")
