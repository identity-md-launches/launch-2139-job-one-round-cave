# Candidate Additions

Review whether line-count increases made by either contributor survive in a
**separately supplied candidate directory**, including manually resolved merges.
Missing new files (even empty ones) also enter the review queue. It reads all
four trees and never changes them or executes their contents.

Run from the workspace root with Python 3.10+:

```sh
python3 -B line-1/tools/candidate-additions/candidate_additions.py --demo
```

Observed: the complete candidate was `checked`; omitting the other contributor's
line and omitting a newly added empty file both returned `review`. The demo exits
0 when those expected outcomes occur. No network or package installation is needed.

For your own stable UTF-8 trees:

```sh
python3 -B line-1/tools/candidate-additions/candidate_additions.py BASE_DIR OURS_DIR THEIRS_DIR CANDIDATE_DIR
```

These must be existing directories inside the current workspace. All regular
files are included, with no implicit exclusions. Keep reports outside input
trees; redirecting onto an input file would truncate it before Python starts.
Exit **0** means no addition-count or added-file flag, **1** means review is
needed, **2** means invalid input (no partial JSON on stdout). A 0 is not merge
approval. Paths are JSON-escaped; source text is represented by hashes and counts.
Hashes of guessable lines are not confidential.

## How it works

For each path, count exact lines, retaining CRLF and final-newline differences.
For every line whose count in either branch exceeds its base count, require the
candidate to contain at least the greater branch count. Thus an old occurrence
cannot hide the loss of a newly duplicated occurrence. Equal additions in both
branches are required once, not summed. A newly introduced file must be present,
even if empty. Missing candidates are checked rather than silently skipped.

The JSON `candidate-additions/v1` report includes exact-byte manifests for all
four inputs, per-file candidate hashes, totals and deterministic review rows.
`added_by` identifies branches with count growth; it does not establish authorship.
The candidate is read directly; no merger is run, and an unresolved textual
conflict does not prevent an addition-count review. Any file/directory collision
across inputs blocks that path and descendants conservatively.

## Checks and limits

```sh
python3 -B line-1/tools/candidate-additions/test_candidate_additions.py
```

All 13 focused tests passed. They include a trial copying the inherited real
Threeway README into four scratch trees: keeping both independent additions
passed; removing one returned exit 1 and named its branch. Source bytes stayed
unchanged and changing the candidate changed its manifest. The 25 inherited
Tree Review tests also passed.

This is a conservative count review, not a semantic merge: reordered or renamed
contributions, intentional replacements and competing choices need a person.
Net-zero moves and additions offset by identical deletions are invisible.
Ordering, deleted text, candidate-only additions, conflict markers, syntax and
meaning are outside its checks. Pair with Deletion Audit for count reductions.

The standard-library tool reuses `tree-review` snapshots/manifests, which import
`merge-review` and `threeway`. Keep those sibling folders if copying it elsewhere.
Bounds: 128 files and 256 directories per tree, nesting depth 16, 1 MiB and 4,000
lines per file, **8 MiB total across all four trees**. The inherited reader's
budget error says “three trees”; the budget here is shared across all four.
Symlinks, special files, invalid UTF-8, NUL and parent traversal are rejected.
Inputs must stay stable and trusted during reading: no atomic snapshot or
protection against concurrent path replacement is provided.
