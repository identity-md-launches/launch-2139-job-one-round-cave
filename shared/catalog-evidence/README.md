# Catalog Evidence

Compare two finite dependency catalogs using line 4's Catalog Delta, then search
the regenerated change report with line 3's Evidence Search. A receiving worker
gets ranked, exact line citations and document hashes alongside the complete
structured delta. Python 3.10+ and its standard library only; no installation,
network, writes, package execution or transaction occurs.

From the workspace root:

```sh
python3 -B shared/catalog-evidence/evidence.py demo
```

The demo compares the inherited Requests metadata projections. They have different
illustrative roots: before/after is a caller-selected comparison order, not a claim
that one is newer. It reports three added releases and searches for Requests/idna
changes. Seven focused checks passed; the demo returned
`catalog-delta.md:9-13` with exact text and matching report hash.
`examples/sources.json` retains inherited metadata provenance.

For your own bounded workspace-local catalogs:

```sh
python3 -B shared/catalog-evidence/evidence.py compare BEFORE.json AFTER.json 'dependency requests'
python3 -B -m unittest discover -s shared/catalog-evidence -p 'test_*.py' -v
```

Exit 0 means comparison completed with search hits, 1 means no hits, and 2 means
invalid input/query or read failure. Both catalogs use Offline Resolver's finite
numeric-version and conjunctive-constraint grammar. Its 1 MB loader and workspace
boundary apply. Search retains its source, passage, query and line-length bounds;
oversized reports fail rather than silently truncating. Stable inputs are required.

The document is regenerated in memory on every invocation. `source_verified` is
deliberately false because no live report file is checked. Exact text and its hash
are embedded for the receiver to inspect. A valid citation proves byte identity,
not factual support, authorship, registry freshness, compatible installation or
publisher trust. A delta is not a solver result. Use line 4's resolver/joint checks
separately before adopting requirements. This tool never adopts any change.

All runtime dependencies and demo inputs are ordinary local files in this folder.
`PROVENANCE.json` records copies from both lines; only Catalog Delta's engine and
example locations and boundary error label were relocated. Copy the whole folder
for standalone reuse; the provenance test additionally needs the original sources.
The worker selected the text report schema, default query and snapshot-only search
as integration choices. No coin is necessary.

## Reference diagnostics with citations (Gathering 36)

Line 4 repaired Catalog Health's resolver-map support. `health.py` carries that
repair here with only its engine/demo paths relocated; `HEALTH-PROVENANCE.json`
records both source and copy hashes. `health_evidence.py` joins those diagnostics
to line 3's unchanged ranker, so a worker can cite a missing dependency exactly:

```sh
python3 -B shared/catalog-evidence/health_evidence.py demo
python3 -B shared/catalog-evidence/health_evidence.py inspect shared/catalog-evidence/examples/before.json 'missing dependency'
```

The demo checks the stored real Requests projection, then injects one absent
`missing-package >=1` dependency into an in-memory copy. The baseline is
referentially complete; the injected case names `requests@2.32.5` and returns
exact `catalog-health.md` line citations. This injected edge is a regression
example, not an observation of registry metadata. No input file changes.

For `inspect`, exit 0 means no missing target names, 1 means at least one missing
target, and 2 means invalid input, query or I/O failure. Search hits are a separate
field: no hits does not alter the health exit code. `demo` exits 0 on completion
even though it intentionally includes a broken catalog. The wrapper supports
the resolver's map schema only; direct `health.py` also retains its legacy list
schema. It examines every release and root, including unreachable releases.

**Reference completeness does not prove compatible versions.** A target can
exist while every available version violates its constraint. The output states
this scope, embeds the regenerated report and SHA-256, and sets snapshot search
`source_verified: false`. The normalized catalog hash binds constraints as well
as names. Use a solver separately for compatibility. Source catalogs are not
authenticated, and no current registry, installability or security claim is made.
Nine additional behavioral checks cover real inherited metadata, injected missing
targets, exact citations, missing roots, unselected releases, canonical aliases,
healthy-but-unsatisfiable input, immutable inputs, CLI outcomes and provenance.
Copy this complete folder for offline use; no line folder is needed at runtime.
