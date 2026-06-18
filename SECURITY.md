# Security Policy

We take the security of Valqore and of the people who run it seriously. This
document explains how to report a vulnerability and what you can expect from us.

## Reporting a vulnerability

**Please do not open a public issue for security reports.** Use one of these
private channels:

1. **GitHub private vulnerability reporting** (preferred) — on this repository,
   go to **Security → Report a vulnerability**. This opens a private advisory
   only you and the maintainers can see.
2. **Email** — `security@valqore.io` (or `tunc@valqore.io`). Encrypt with our
   PGP key if you prefer; request it in a first, low-detail message.

Please include, where possible:

- The affected component and version (e.g. `valqore/engine:1.5.0`, the CLI, the
  admission webhook, the MCP gate).
- A description of the issue and its impact.
- Steps to reproduce, a proof of concept, or a failing test case.
- Any suggested remediation.

## What to expect

We are a small team and will be honest about timelines rather than promise SLAs
we cannot meet:

| Stage | Target |
|---|---|
| Acknowledge your report | within **3 business days** |
| Initial assessment + severity | within **10 business days** |
| Fix or mitigation plan shared with you | depends on severity; critical issues are prioritized immediately |
| Public disclosure | coordinated with you, normally after a fix ships |

We will keep you informed through the process and credit you in the advisory and
release notes unless you ask us not to.

## Coordinated disclosure

We follow coordinated disclosure. We ask that you give us a reasonable window to
ship a fix before any public discussion, and we commit to working the issue
promptly and transparently in return. We will publish a GitHub Security Advisory
(and CVE where applicable) when a fix is available.

## Safe harbor

We will not pursue or support legal action against researchers who:

- Make a good-faith effort to follow this policy;
- Test only against their **own** Valqore deployments and data (Valqore is
  self-hosted — there is no Valqore-operated SaaS to test against);
- Avoid privacy violations, data destruction, and service degradation; and
- Give us reasonable time to respond before disclosure.

Activity consistent with this policy is considered authorized; we will help
clarify scope if you are unsure before you act.

## Scope

In scope: the Valqore engine image, the CLI, the Kubernetes admission webhook,
the MCP gate, the agent-action gate, the approval/journal subsystem, and the
license/activation mechanism.

Out of scope: findings that require a compromised host or root on the machine
running Valqore; social engineering; and issues in third-party dependencies that
are already publicly known (report those upstream — though we still want to know
which version we ship them in).

## Supported versions

Security fixes are issued for the **latest released minor version** of the
engine. Please reproduce on the latest `valqore/engine` tag before reporting.

## Supply-chain verification

Every published image is cryptographically signed and ships an SPDX SBOM so you
can verify exactly what you run. See **"Verify image authenticity"** in the
[README](README.md) for the `cosign verify` and `cosign verify-attestation`
commands.

## A note on no bug-bounty (yet)

We do not currently run a paid bug-bounty program. We deeply value reports and
will credit you publicly. If that changes, this document will say so.
