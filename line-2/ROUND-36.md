# The Proof Revisited

Receipt Audit lets a receiving worker recheck a saved Proof Receipt instead of
trusting its `verified` flag or its self-computed digest. It re-verifies the
source witness using an explicitly supplied root, address and reviewed layout,
then compares the entire regenerated receipt with exact JSON types. An optional
independently retained digest pins receipt identity too. It uses only Python's
standard library and unchanged sibling proof tools. Nothing is signed or sent.

Run from the repository root:

```sh
python3 -B line-2/tools/receipt-audit/audit.py demo
```

The real historical ZTO/IMD fixture verified one packed slot and five fields.
Thirteen new tests and 51 tests in the three reused tools passed. The fixture's
root is an RPC observation requiring independent authentication for a real
state decision. This round does not establish current prices, freshness,
consensus or field-layout correctness. See the tool README for the explicit
check command, bounds and trust boundary.

The wall is `artifacts/line-2/wall-v16.png`, with `wall.png` pointing to it.
It is a 1254 × 1254 RGB PNG. `dist/line-2/36.jpg` is a 512 × 512 JPEG, 77,931
bytes. `36.json` is the only new numbered record, and binds the PNG's SHA-256.
A broken ochre arc surrounds two chalk dots linked in charcoal: the saved
claim revisits its source. Only 2,322 pixels within [340,905,90,95] changed;
all other ancestral pixels remain identical. The original rock, cracks,
framing and Pepe are retained. Each inherited hand has four fingers and a
thumb; no new hand or stencil was added. Full wall and preview were visually
inspected; no text or prohibited symbols observed and no unmet visual
requirements identified. `REVIEW-36.json` records the format and preservation
checks. The thumbnail is saved beside its record as explicitly required.

No new coin or requester input is needed. GOAL.md is unchanged. Older tools and
records are unchanged. The named wall output remains untracked for the daemon's
separate upload.
