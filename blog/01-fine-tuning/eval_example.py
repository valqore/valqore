"""Example: how to evaluate a fine-tuned model with factual checks.

Build your eval suite BEFORE training — it's the spec, training is the implementation.
"""

from dataclasses import dataclass


@dataclass
class TestCase:
    id: str
    category: str
    prompt: str
    checks: list[tuple[str, str]]  # (check_name, substring_to_find)


# Example test cases (simplified from our 25-test suite)
TEST_CASES = [
    TestCase(
        id="rule-001",
        category="rule_knowledge",
        prompt="Explain rule SP-006 and its severity.",
        checks=[
            ("mentions_root", "root"),
            ("mentions_severity", "critical"),
            ("has_fix", "runAsNonRoot"),
        ],
    ),
    TestCase(
        id="halluc-001",
        category="hallucination",
        prompt="What does Valqore rule XY-999 check for?",
        checks=[
            ("admits_unknown", "not a real"),  # Must NOT make up an answer
        ],
    ),
]


def evaluate_response(response: str, checks: list[tuple[str, str]]) -> tuple[int, int]:
    """Check if response contains expected substrings."""
    passed = sum(1 for _, substr in checks if substr.lower() in response.lower())
    return passed, len(checks)


# Usage:
# response = ollama.generate(model="valqore", prompt=test.prompt)
# passed, total = evaluate_response(response, test.checks)
# print(f"{test.id}: {passed}/{total} checks passed ({passed/total:.0%})")
