# Lesson 04: Fix a real formatter bug with regression tests

**Project:** [GDScript Toolkit](https://github.com/Scony/godot-gdscript-toolkit) (Python tooling for Godot)
**Issue:** [#394: warning annotations become invalid formatted code](https://github.com/Scony/godot-gdscript-toolkit/issues/394)
**Proposed fix:** [PR #435](https://github.com/Scony/godot-gdscript-toolkit/pull/435)
**Snapshot:** November 17, 2026. PR open for review; not merged. Upstream GitHub Actions requires maintainer approval.

## 1. Understand the failure

The input is valid as reported by the issue author:

~~~gdscript
@warning_ignore("integer_division")
const VELOCITY_TIMEOUT := 1000 / 5
~~~

The existing formatter could place both statements on the same line:

~~~gdscript
@warning_ignore("integer_division") const VELOCITY_TIMEOUT := 1000 / 5
~~~

The issue reports that Godot rejects this output because the warning annotation must have its own line. A separate example involved @warning_ignore before an @export variable.

**Important distinction:** the toolkit's own Lark parser accepted both strings during our investigation. A successful parse in one implementation does not prove that another implementation (Godot's GDScript parser) accepts the output.

## 2. Trace the real mechanism

The formatter collects syntax-tree annotations in a context object. When it formats the next statement, it asks whether the collected annotations and statement fit onto one line.

~~~text
GDScript source
      |
      v
Parser creates syntax trees
      |
      v
Formatter accumulates annotations
      |
      v
Can it combine this annotation and declaration?
      |
  yes | no
      v
Inline output or separate lines
      |
      v
Formatted GDScript
~~~

The missing condition was not line length. It was whether an annotation was **legal to combine**, regardless of the line's width.

## 3. Make the test fail first

Three previously untested patterns joined incorrectly:

- Warning annotation followed by @export var.
- Warning annotation followed by const.
- Warning annotation followed by var.

We added assertions that the warning annotation must end with a newline. **Before the change: 3 failed, 3 pre-existing standalone cases passed.** The test suite therefore identified the actual behavior instead of merely failing to import a dependency.

Inspect [the regression test](https://github.com/Scony/godot-gdscript-toolkit/pull/435/files) in PR #435.

## 4. Fix just the decision

In gdtoolkit/formatter/annotation.py, the one-line formatting condition now contains:

~~~python
and not any(
    annotation.children[0].value == "warning_ignore"
    for annotation in context.annotations
)
~~~

Read this from the inside out:

- context.annotations is the collected list.
- Each annotation has a syntax-tree node whose first child identifies the annotation name.
- any(...) returns True when at least one is warning_ignore.
- not reverses that result: **only combine lines when there is no warning_ignore annotation**.

The existing annotation classification and other formatting behavior were not replaced.

## 5. Verify the fix

| Check | Observed result |
| --- | --- |
| New failing declaration cases after fix | 3/3 passed |
| Original standalone warning-annotation cases | 3/3 passed |
| Formatter basics | 4/4 passed |
| Existing formatter input/output fixtures | 117/117 passed |
| Combined local formatter checks | **127/127 passed** |
| Toolkit parser and safety checks on new cases | Passed |
| Godot runtime parser | **Not run** |
| Upstream CI | Awaiting maintainer approval to run |

A missing dependency initially prevented the parser from starting. That was an **environment error**, not proof of the formatter bug. We resolved it before counting test failures. The test environment used the official Lark 1.2.2 source and a compiled regex package from PyPI.

This is why a useful bug report distinguishes **failed setup**, **reproduced failure**, **passing unit test**, **native runtime**, and **maintainer acceptance**.

## 6. Your hands-on practice

From a local checkout of GDScript Toolkit, with a Python environment containing its dependencies and pytest:

~~~shell
python -m pytest -q tests/formatter/test_issue_394_warning_annotations.py
python -m pytest -q tests/formatter/test_input_output_pairs.py
~~~

Try the following in a **throwaway feature branch**, not in the main branch:

1. Find the new guard in annotation.py and temporarily remove it.
2. Run the issue-specific tests. Identify the three expected failures.
3. Restore the guard and run those tests again.
4. Add another regression involving multiple annotations before a declaration.
5. Explain why the toolkit's parser can accept output that the Godot engine reports as invalid.

## 7. Understand the contribution gate

The patch is publicly proposed at [PR #435](https://github.com/Scony/godot-gdscript-toolkit/pull/435). GitHub marked its upstream CI run as **action_required**, a maintainer-side approval gate for a contributor workflow. No one should infer CI passed from local tests, or infer that a submitted PR has been merged.

**Engineering principle:** the point of a contribution is not the count of PRs. It is producing a minimal, testable change with explicit boundaries around what has and has not been verified.
