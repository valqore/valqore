# Precision run — three real repositories

The benchmark next door measures **coverage**: how many domains Valqore can see
at all, against a five-file corpus written to be broken. It answers *"what can
you find"*.

It does not answer the question a staff engineer actually asks, which is
**"how much of what you find is wrong"**. This page answers that one, on code
nobody wrote for us, and it is not flattering.

## What was scanned

| Repository | What it is | Commit | Scanned |
|---|---|---|---|
| [`GoogleCloudPlatform/microservices-demo`](https://github.com/GoogleCloudPlatform/microservices-demo) | Google's reference microservices app | `c7cb6d5` (2026-10-27) | `kubernetes-manifests/` |
| [`argoproj/argo-cd`](https://github.com/argoproj/argo-cd) | CNCF graduated; this one file installs Argo CD into thousands of clusters | `a74a3f8` (2026-11-22) | `manifests/install.yaml` |
| [`terraform-aws-modules/terraform-aws-vpc`](https://github.com/terraform-aws-modules/terraform-aws-vpc) | the most-downloaded AWS Terraform module | `577ad62` (2026-11-17) | module root, `--iac terraform` |

Engine v1.19.0, plain `valqore evaluate` — no `--compliance-pack`, no
`--categories`. That is deliberate: the default is what a first-time user runs.

## Before a single finding could be counted, the run hit two defects

**The Terraform scan produced no output at all.** Not a bad verdict — nothing,
for two separate reasons:

1. The Terraform parser opened `.tf` files with the platform's default
   encoding. `outputs.tf` in terraform-aws-vpc is valid UTF-8 and contains a
   Cyrillic *es* where upstream meant to type a `c` — "Publiс Subnets". On
   Windows, cp1252 has no byte `0x81`, so two of the module's files were
   skipped with a warning.
2. `tags = merge(var.tags, ...)` parses to a **string** — the HCL library
   returns the unevaluated expression, because resolving it needs a plan — and
   the parser passed that string through as the resource's label map. Region
   auto-detection then called a dict method on it and raised, *after every rule
   had already been evaluated*. The scan died on the way to printing its
   results.

Both are fixed, with tests that fail against the unfixed parser. **They are not
yet in a released image**, so until the next release the Terraform run below
reproduces the crash rather than the table.

What this cost is the point. The most downloaded AWS module there is could not
be scanned at all, and we did not know, because no test and no benchmark had
ever pointed the engine at a repository it did not own.

## What the scan found

| | resources | rule evaluations | findings | findings per resource |
|---|---:|---:|---:|---:|
| microservices-demo | 12 | 11,582 | **1,936** | 161 |
| argo-cd | 29 | 22,333 | **3,172** | 109 |
| terraform-aws-vpc | 123 | 175 | **17** | 0.14 |

The asymmetry is itself a result. On Kubernetes the engine says about a hundred
things per resource; on Terraform it says almost nothing. One of those numbers
is wrong, and probably both.

## Noise, counted mechanically

These buckets are decided by each finding's own message, so anyone with the
JSON can re-derive them. They are a **lower bound** — they catch only what is
detectable from the text.

| | microservices-demo | argo-cd | terraform |
|---|---:|---:|---:|
| **Engine errors shown as findings** — a rule raised an exception and the exception was reported as a MEDIUM finding, with a severity and a resource | 22 | 12 | 0 |
| **"No data available"** — needs live telemetry a static scan never had | 189 | 378 | 1 |
| **"Not declared"** — demands a governance annotation: CRA security contact, DORA criticality tier, FOCUS dataset version | 445 | 725 | 0 |
| **Duplicates** — a second or third rule restating a fact already reported | 190 | 310 | 0 |
| **Subtotal: not a finding** | **846 (44%)** | **1,425 (45%)** | 1 (6%) |

Worst single repetition: *"No CRA security-contact declared"* fires **51 times**
on argo-cd — once per resource, for one fact about the publisher.

Worst duplication: seven cost-allocation rules report the same missing label
set, 252 findings on argo-cd where 42 would say it. Four separate rules report
that an image is not pinned to a digest.

## Hand triage: terraform-aws-vpc, all 17

Small enough to do properly, so every finding was checked against the file.

| Rule | Finding | Verdict |
|---|---|---|
| `TF-001` ×3 | local state, configure a remote backend | **False.** A child module must not declare a backend; Terraform forbids it |
| `TF-013` ×3 | OpenTofu state encryption not configured | **False.** Same reason |
| `TF-011` ×2 | no `.terraform.lock.hcl` | **False.** The lock file belongs to the root module; a published module should not ship one |
| `TF-007` ×2 | no `required_version` constraint | **False.** `versions.tf` line 2: `required_version = ">= 1.0"` |
| `TF-017` ×2 | no `required_version` pin | **False.** Same line |
| `AWS-020` | IAM password policy does not enforce 90-day expiration | **False.** Fired on an IAM *role*. There is no password policy in a VPC module |
| `AWS-175` | role has never been used, or `last_used_date` unavailable | **False by construction.** `last_used_date` is a runtime fact — unavailable in every static scan that will ever run |
| `AWS-167` | policy document Version is `''`, expected `2012-10-17` | **False.** It is a `data.aws_iam_policy_document`, which renders the version; `actual: ""` means not found, not wrong |
| `AWS-168` | IAM role has no tags | **False.** `vpc-flow-logs.tf:89` — `tags = merge(var.tags, var.vpc_flow_log_tags)` |
| `AWS-163` | `max_session_duration` not set | **True**, and advisory. A service role assumed by `vpc-flow-logs.amazonaws.com` does not need one |

**1 of 17 true. Sixteen false positives, from four causes:** a reusable module
judged as if it were a root configuration (10), a runtime fact asserted about
static code (1), a rule applied to the wrong resource type (1), and a value the
parser could not resolve reported as a value that is absent (4).

Note how little the mechanical bucketing caught here — 1 of 17, against 16 by
hand. Applicability is invisible in the message text. **The real false-positive
rate is higher than the measured one in every table on this page.**

## One finding whose evidence is wrong

`NET-011` on microservices-demo: *"Pod 'adservice' has no labels and no
NetworkPolicy — fully open to cluster traffic."*

`adservice.yaml` carries `labels: {app: adservice}` on both the Deployment and
the pod template. The conclusion is right — there is no NetworkPolicy — and the
stated reason is false. That is the most expensive kind of wrong: a reader
checks the first clause, finds it untrue, and discounts the other 1,935.

## What we think this says

The engine is not imprecise in the ordinary sense. Most of the rules that fired
report something true about the file in front of them. The problem is that the
default **answers every question at once, for every resource, under every
regulation**, and no one can find the four findings that matter inside a
hundred per resource.

Four changes would move the number more than any rule edit:

1. **An error is not a finding.** 34 rule exceptions were rendered as MEDIUM
   findings, indistinguishable from a verdict.
2. **"No data available" is not a finding.** A `NOT_ASSESSED` outcome already
   exists; 567 of these arrived as FAIL or WARN instead.
3. **A fact about the publisher belongs to the scan, not to every resource.**
4. **Deduplicate before display.** Four rules, one digest.

## Reproducing this

```bash
git clone --depth 1 https://github.com/GoogleCloudPlatform/microservices-demo
git clone --depth 1 https://github.com/argoproj/argo-cd
git clone --depth 1 https://github.com/terraform-aws-modules/terraform-aws-vpc

valqore evaluate microservices-demo/kubernetes-manifests -o json > a.json
valqore evaluate argo-cd/manifests/install.yaml           -o json > b.json
valqore evaluate terraform-aws-vpc --iac terraform        -o json > c.json

python benchmarks/precision/triage.py a.json microservices-demo
python benchmarks/precision/summarise.py a.json microservices-demo
```

Commits are pinned in the table above, so the corpus is fixed even though the
repositories move. Counts will drift as rules change; the method will not.

If your own numbers differ from ours, we would rather hear it than not —
[open an issue](https://github.com/valqore/valqore/issues).

---

Run 2026-11-22 · engine v1.19.0 · Windows 11, Python 3.13.
