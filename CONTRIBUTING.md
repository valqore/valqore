# Contributing to Valqore

Thank you for your interest in Valqore. This is a **documentation-only public repository** — the production codebase is maintained privately. Contributions here focus on feedback, discussion, use-case documentation, and community rule proposals.

---

## Ways to Contribute

### 1. Report Issues and Bugs

If you are an early-access user and encounter unexpected behaviour, please open a [GitHub Issue](https://github.com/valqore/public/issues) with:

- A clear description of what you expected vs. what happened
- The cloud provider and resource type involved
- The verdict you received and why you believe it is incorrect
- Any relevant context (cluster version, Terraform provider version, etc.)

We do not require you to share infrastructure details — describe the shape of the problem, not the sensitive specifics.

### 2. Suggest New Rules

Valqore's rule engine is extensible. If you have identified a class of infrastructure misconfiguration, security risk, or carbon inefficiency that Valqore does not currently detect, open an issue with the label `rule-proposal` and include:

- **What to detect** — describe the condition (e.g., "pods with no memory limit in a namespace with no LimitRange")
- **Why it matters** — the risk or cost impact if the condition is undetected
- **Suggested severity** — should this be `BLOCK` or `PASS_WITH_MONITORING`?
- **References** — links to relevant documentation, CVEs, CIS benchmarks, or CNCF guidance

Rule proposals from the community will be reviewed, discussed publicly in the issue thread, and — if accepted — added to the roadmap.

### 3. Improve Documentation

Corrections, clarifications, and additions to any `.md` file in this repository are welcome. Open a pull request with a brief description of what you changed and why.

Good areas for community contribution:

- Additional use-case examples in [docs/use-cases.md](docs/use-cases.md)
- Corrections to GreenOps methodology in [docs/greenops.md](docs/greenops.md)
- Questions or clarifications in [docs/how-it-works.md](docs/how-it-works.md)

### 4. Share Your Experience

If you are using Valqore (or evaluating it), we would love to hear about your context:

- What cloud providers and orchestrators are you running?
- Which rule categories matter most to your team?
- What compliance or sustainability goals are you working toward?

Open a [GitHub Discussion](https://github.com/valqore/public/discussions) to share context. These conversations directly influence the roadmap.

### 5. Spread the Word

The most impactful thing you can do right now is help the community discover Valqore:

- Star this repository
- Share the project on LinkedIn, Reddit (r/devops, r/kubernetes, r/FinOps), Hacker News, or Dev.to
- Mention Valqore in conversations about AI-Ops safety, FinOps governance, or cloud sustainability

Community visibility directly supports Valqore's ability to grow and attract contributors.

---

## Code of Conduct

All interactions in this repository are expected to be respectful, constructive, and professional. Harassment, discrimination, and bad-faith contributions will result in removal.

---

## Contact

- Website: [valqore.io](https://www.valqore.io)
- LinkedIn: [linkedin.com/company/valqore](https://www.linkedin.com/company/valqore)
- Issues: [GitHub Issues](https://github.com/valqore/public/issues)
- Discussions: [GitHub Discussions](https://github.com/valqore/public/discussions)

---

## Trademark Notice

VALQORE is a pending trademark. Use of the name in derivative works, forks, or competing products is not permitted without explicit written permission.
