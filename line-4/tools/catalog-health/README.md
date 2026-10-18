# Catalog Health

Catalog Health checks a finite Offline Resolver catalog for references to
packages absent from its `packages` map. It checks every release's
dependency-to-constraint map and the root requirements, using the resolver's
name normalization and input grammar. A report identifies each missing target,
its source and its constraint. It does not search for a compatible selection:
`healthy: true` means the catalog is valid and its targets exist, not that its
requirements are satisfiable.

The earlier `packages`-only format with `dependencies` lists remains accepted
for existing callers. It is checked separately and never used to interpret a
resolver catalog with `roots`; a resolver catalog containing list metadata is
rejected as invalid.

Run from the repository root; this one command checks the committed finite
Requests metadata projection:

```sh
python3 -B line-4/tools/catalog-health/health.py demo
```

I ran it here: it reported five packages, ten releases, zero missing targets,
and `healthy: true`. A regression test adds an absent `missing-package` target
to that same real projection and confirms the checker reports it; the inherited
resolver independently reports that target as a dead end.

For a catalog in the current workspace, run
`python3 -B line-4/tools/catalog-health/health.py CATALOG.json`.
The tool uses Python 3.9+ and only the standard library. It reads at most 1 MB
through the resolver's workspace-bound loader; it does not fetch metadata,
install packages, or execute package code. Exit status 0 means all targets
exist, 1 means at least one is missing, and 2 means invalid input or a read
error. Its validation depends on Offline Resolver's grammar and loader.
