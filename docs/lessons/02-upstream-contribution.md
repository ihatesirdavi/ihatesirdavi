# Lesson 02: A real open-source pull request

**Project:** [GarrettGunnell/AcerolaFX](https://github.com/GarrettGunnell/AcerolaFX)
**Issue:** [#63, README before/after links are dead](https://github.com/GarrettGunnell/AcerolaFX/issues/63)
**Submitted change:** [PR #64](https://github.com/GarrettGunnell/AcerolaFX/pull/64)
**State when recorded:** Open for maintainer review; not merged.

## 1. Understand the symptom

The README had two links to interactive gameplay and gpose comparison albums. A browser could follow those addresses, but their current destination was an unrelated MeshBlend website.

The critical distinction is between transport success and task success. The final site returned HTTP 200; that did not establish that the comparison gallery was available.

A useful test checks the redirect destination, not only the status code:

~~~powershell
curl.exe -L -sS -o NUL -w 'final=%{url_effective} code=%{http_code}' 'https://imgsli.com/MTE0MTg3/0/1'
~~~

Observed destination at the time of the repair: https://meshblend.lervik.com/ (HTTP 200).

## 2. Inspect before editing

We read the upstream README, its examples directory, the open issue, and the MIT license. The repository already contained seven example screenshots. It did **not** contain the original paired before/after images, so claiming to restore interactive comparison data would be misleading.

There were no open upstream PRs at the time of inspection.

## 3. Make the smallest defensible change

We forked the repository, cloned it locally, and created the branch:
docs/issue-63-dead-comparison-links

The patch removes just the two dead README links and tells readers that the static examples remain available. The original screenshots and shader code are unchanged.

The diff contains **one added line and three removed lines** in README.md. Small changes are easier to reason about and review.

## 4. Test what can actually be tested

- Both original URLs were checked live and redirected away from the intended gallery.
- The patched README contained no remaining imgsli links.
- All seven existing example files were checked and remained referenced by the README.
- git diff --check passed.

We did **not** run shader runtime or visual tests because this patch does not change shader code. It does not restore the original comparison pairs.

## 5. Learn from an actual failure

The first text replacement failed because the Windows checkout's line endings differed from the expected single LF newline pattern. We corrected it by matching the exact link text while allowing intervening whitespace, with a single expected occurrence.

Lesson: **a logically correct transformation can fail when its assumptions about file format are wrong**. Always check the original bytes and enforce the expected match count before writing.

## 6. The real contribution cycle

~~~text
Upstream issue
   ↓ reproduce
Fork (your account)
   ↓ feature branch
Minimal change
   ↓ verify
Commit + push
   ↓
Upstream pull request
   ↓ maintainer review
Merge, revision request, or rejection
~~~

A submitted PR is evidence of participation, not proof the maintainer accepted a fix.

## 7. Your practice

1. Open PR #64 and use the Files changed tab to identify the exact lines changed.
2. Explain why an HTTP 200 response was insufficient evidence of a working link.
3. Explain why we did not attempt to fabricate missing before/after images.
4. Inspect the commit history and locate the fork branch and upstream base branch.
5. Propose one test that would catch the same class of bug in another repository without blocking legitimate redirects.

**Next coding lesson:** investigate a small executable bug with a regression test before changing its implementation. We will check the next project's contribution rules first.
