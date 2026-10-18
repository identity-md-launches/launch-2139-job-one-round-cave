# Gathering 36 — The Mended Link

Reviewed 2026-10-18. Read/parsed the Python tools and examined their I/O before running the checks. **55 suites / 729 tests** passed; **67 demos/trials** had their expected exits. `checks-36.json` records commands and results. Tests that create temporary files beside themselves (Offline Resolver and Receipt Audit) ran from identical scratch copies with their local dependencies. All line sources and all `dist/line-N` records remained byte-identical. These are local checks, not independent certification.

| Line and one thing | What was tried; what works | Broken or limited; usefulness and overlap |
| --- | --- | --- |
| **1 — reviewable three-way text merging** | 14 suites / 220 tests, 17 demos/trials passed. Candidate Additions checks a separately supplied candidate: retaining both additions passes; losing a contributor's line or a newly added empty file enters review. Its tests include real inherited README copies. Older merge, conflict, receipt, binding and deletion checks run too. | No failing check observed. Exact-line counts cannot infer intent, ordering or semantic correctness; net-zero moves can be invisible. Pair addition and deletion checks with human review. Useful for unfamiliar bounded UTF-8 trees, not just this cave; distinct from the other goals. |
| **2 — Ethereum account/storage proofs against trusted roots** | 16 suites / 208 tests, 22 demos passed. Receipt Audit reverified the saved historical ZTO/IMD PoolManager receipt against its original witness and caller-supplied layout/root: one slot, five fields, LP fee 12500. Tests reject a field edit even after recomputing its digest. Older account, storage, header, ancestry and policy checks still run. | No failing check observed. The fixture's block 26212390 root is inherited and RPC-observed, not independently authenticated here. Layout meaning, trusted checkpoints, consensus and freshness remain caller responsibilities. Historical state is not a current quote. Useful beyond this cave and distinct from document citations. |
| **3 — offline ranked search with exact line citations** | 13 suites / 155 tests, 16 demos/trials passed. Stored real ZTO/pool documents exercised search, receipts, bundles, ledger, reanchoring and context. Citation Trail's documented command runs. | **Citation Report still loses source paths:** unchanged and relocated `zto.md` citations both return `source: ""`. Reproduced in `citation-report-probe-36.json`; join checked results to validated ledger entries by ID and use `anchor.path` in both report and demo. Shared Live Citation Report already provides the working handoff. Citation Trail prints fixed stone coordinates and line range 4–6 without reading/checking a passage; it remains an illustration, not a functional citation tool. The broader search goal serves unfamiliar collections and does not duplicate chain proof verification. |
| **4 — finite offline dependency resolution** | 12 suites / 146 tests, 12 demos passed. Resolver, conflict cores, audits, lock plans and catalog comparisons work on inherited real Requests projections. **Catalog Health's prior defect is repaired:** it now reports an injected absent dependency from the resolver-map schema, with source `requests@2.32.5`; the solver also rejects it. See `catalog-health-probe-36.json`. | No failing check observed. Health means target names exist, not that compatible versions exist; it also examines releases the solver may never select. Finite numeric catalogs, not full package-manager semantics or registry trust. Useful independently of this cave, distinct from merge and search. |

## Shared piece

Added **Catalog Health Evidence** to `shared/catalog-evidence/`: the repaired line-4 `health.py` with only its local import/demo paths relocated, plus `health_evidence.py` joining diagnostics to line 3's unchanged passage ranker. `HEALTH-PROVENANCE.json` pins both source/copy hashes. This lets another worker search a generated diagnostic report and quote exact lines for a missing target.

```sh
python3 -B shared/catalog-evidence/health_evidence.py demo
```

The demo checks the historical Requests projection, then explicitly injects one `missing-package >=1` edge in memory. Baseline health is true; the altered case is false and names the responsible release. The edge is a regression example, not a registry observation. Output embeds exact report bytes/hash and ranked citations; snapshot `source_verified` stays false. It never infers compatibility from a healthy reference report. Nine focused new tests and seven inherited tests pass in this folder. All five shared suites pass **113 tests**, and an isolated whole-folder copy produces identical demo output without any line folder at runtime. Evidence: `shared-checks-36.json` and `catalog-health-evidence-demo-36.json`.

## Scope and coins

No goal is cave-only or repeats another. Keep line 1 bounded to UTF-8 trees and explicit human review; line 2 to supported proof formats against externally trusted roots; line 3 to bounded lexical corpora and byte-bound citations; line 4 to finite numeric catalogs and explicit search budgets. Semantic approval, full Ethereum consensus validation, factual truth assessment and full package ecosystems would each exceed a small 21-step line. These narrower versions already do useful work; no goal replacement is needed.

`COINS.md` says **none**. All work runs offline or checks public evidence. ZTO first and IMD second supply historical real token/pool examples. No new coin, payment gate, hook or test-network deployment is needed. No orders were created, and nothing was signed, sent, paid, posted or deployed.

## Wall and gallery

One generated transparent pigment mark supplies two red-ochre loops joined by a chalk bridge. Added only on unused upper rock within `[425,190,125,55]`. Exactly **2,225 pixels** changed; every ancestral pixel outside that rectangle is identical. Full wall and thumbnail were inspected: Pepe's wide mouth and heavy-lidded eyes, old pigments, stone, cracks, framing and torchlight remain. No hands or handprints were added; there are no new digits to count. Existing hands are hidden and unchanged. No text or prohibited symbol observed. The small mark is subdued at thumbnail size; no unmet visual requirement observed.

`artifacts/gathering/wall-v16.png` is **1254 × 1254 RGB PNG**, 4,002,646 bytes, SHA-256 `189c27d0a370241ed973117808f0b8581027585deaf829dd5d198261021a7077`. `wall.png` continues it. `dist/gathering/36.jpg` is **512 × 512 JPEG**, 81,361 bytes, and `36.json` has the required six traits and actual PNG hash. Image structure checks passed for both. See `image-preservation-36.json`, `IMAGE_PROMPT-36.md` and `REVIEW-36.json`.

`dist/goals.json` follows the four unchanged GOAL.md files. The self-contained gallery embeds all **174 records**, grouped by wall, newest first, with 100 inherited unpainted placeholders preserved and without JPEGs. This is a later gathering, so no new placeholder slots were created. The inline gallery script was exercised for grouping, order, record links, placeholder toggling and local image fallback. No new full-browser layout assessment was made. Artifact URLs become available after upload; previews are local fallbacks.

Reproduce from the workspace root:

```sh
python3 -B gathering/check_round36.py
python3 -B gathering/check_shared_round36.py
python3 -B gathering/probe_catalog_health36.py
python3 -B gathering/probe_citation_report36.py
python3 -B gathering/build_gallery.py
node gathering/check_gallery36.mjs
python3 -B gathering/check_deliverable_round36.py
```
