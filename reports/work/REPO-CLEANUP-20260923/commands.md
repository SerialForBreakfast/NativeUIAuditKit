# Maintainer Git steps

Run one numbered step at a time from the repository root. No agent has run a Git
write. The proposed commit includes the integrated pending work plus cleanup;
cleanup-only staging would leave the new probe test without its dependencies.

## 1. Review the prepared set

```sh
cd /Users/josephmccraw/Documents/GitHub/NativeUIAuditKit
git status --short
git diff --stat
git diff --check
less reports/work/REPO-CLEANUP-20260923/commit-paths.txt
git diff
```

git diff excludes new files: review listed new source/tests/docs in your editor too.
The path list is deliberately fixed, not an expression that sweeps future files.

## 2. Stage the reviewed snapshot

Only after accepting step1:

```sh
git add --pathspec-from-file=reports/work/REPO-CLEANUP-20260923/commit-paths.txt
git diff --cached --stat
git diff --cached --check
git diff --cached --name-only
```

The staged list should contain no generated capture media, run logs or large
per-image inventories. If anything unexpected appears, stop; do not commit.
This stages current contents at those paths, so don't use an old list after other
work has arrived without reviewing it again.

## 3. Commit locally after review

```sh
git commit -m "Improve focus evidence and dataset validation; contain generated artifacts"
git status --short
```

No push, tag or history rewrite included. The artifact files remain on disk ignored.

## Historical tracked artifacts — review only, not removal

```sh
git ls-files -ci --exclude-standard
```

This lists already-tracked paths matching ignores; do not pipe it to git rm.
De-indexing needs a separately reviewed exact list and retained recoverable copies.
Do not run git clean, git rm -r --cached ., filesystem deletion or force-push.
Even a later git rm --cached removes files from future checkouts; existing history
still retains their bytes. A history-size reduction is a separate maintainer decision.
