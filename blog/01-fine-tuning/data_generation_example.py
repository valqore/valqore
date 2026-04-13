"""Example: how to generate training pairs from a rule engine.

This demonstrates the approach — generate Q&A pairs directly from your
rule definitions so the training data IS the source of truth.
"""


def generate_pairs_from_rule(rule: dict) -> list[dict]:
    """Generate multiple training pairs from a single rule definition."""
    pairs = []

    # Type A: Rule explanation
    pairs.append({
        "messages": [
            {"role": "system", "content": "You are a cloud infrastructure governance assistant."},
            {"role": "user", "content": f"Explain rule {rule['id']} and its severity."},
            {"role": "assistant", "content": f"{rule['id']}: {rule['name']} (Severity: {rule['severity']}). {rule['description']} Remediation: {rule['remediation']}"},
        ]
    })

    # Type B: Failure scenario
    pairs.append({
        "messages": [
            {"role": "system", "content": "You are a cloud infrastructure governance assistant."},
            {"role": "user", "content": f"My deployment is failing rule {rule['id']}. Why?"},
            {"role": "assistant", "content": f"Rule {rule['id']} ({rule['name']}) checks: {rule['description']}. To fix: {rule['remediation']}"},
        ]
    })

    return pairs


# Example rule definition (public — this is what rules look like)
example_rule = {
    "id": "SP-006",
    "name": "Container Running as Root",
    "severity": "CRITICAL",
    "description": "Container runs as root (UID 0), allowing full host access on container escape.",
    "remediation": "Set securityContext.runAsNonRoot: true and runAsUser: 1000.",
    "compliance": ["CIS 5.2.6", "SOC2 CC6.1"],
}

pairs = generate_pairs_from_rule(example_rule)
print(f"Generated {len(pairs)} pairs from rule {example_rule['id']}")
