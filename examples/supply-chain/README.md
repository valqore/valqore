# Supply chain — examples

[`unsigned-unpinned.yaml`](unsigned-unpinned.yaml) ships three classic image-reference risks:

- `nginx:latest` — a **mutable tag**; the image behind it can change without you knowing
- `redis` — **no tag at all**, which silently resolves to `:latest`
- `busybox:1.36` — tagged, but **not pinned by digest**

These are how a "known-good" image quietly becomes a different, unverified image at deploy time.

```bash
valqore evaluate unsigned-unpinned.yaml --score
```

Expect a **BLOCK** verdict with failures on the unpinned/mutable references. Pin images by
digest (`image@sha256:…`) to fix them.

> The `valqore` alias is set up in the [repo README Quickstart](../../README.md#quickstart-60-seconds).
