# Contribution evidence and provenance

**Record date:** November 17, 2026. **GitHub account:** [ihatesirdavi](https://github.com/ihatesirdavi). These records describe observed work at the stated commits; statuses may change later.

## Attribution, oversight, and factual checks

- **Agent assistance:** software agents supported research, drafting, code changes, testing, and documentation. This is disclosed unobtrusively in the footer of a contribution rather than presented as its main achievement.
- **Human oversight:** the repository owner defines goals, scope, and permission boundaries, and retains final review and acceptance authority. This records human direction, **not** an unverified claim that every source line received independent human review.
- **Fact-checking:** original repository files, observed command output, issue discussions, checks, and GitHub state were consulted. Automated tests and agent review are not substitutes for owner acceptance, upstream maintainer approval, or native-runtime verification.
- **Evidence language:** proposed, locally tested, CI-verified, merged, and accepted are distinct states. Unrun checks remain marked NOT_RUN.

## Tested environment and public receipts

| Scope | Stack and source | Evidence | Remaining gate |
| --- | --- | --- | --- |
| [Profile](https://github.com/ihatesirdavi/ihatesirdavi) | Python 3.11, unittest, XML/SVG validation, Git/GitHub CLI, GitHub Actions on Ubuntu 24.04 | Seven local tests and [native CI success](https://github.com/ihatesirdavi/ihatesirdavi/actions/runs/44187819784) at commit 1d1308fc2ca1004faea451fc3f48410e2f510caf | Visual browser review is distinct from SVG syntax checks |
| [GDScript Toolkit PR #435](https://github.com/Scony/godot-gdscript-toolkit/pull/435) | Python 3.11.9, pytest 8.3.4, gdtoolkit 4.5.1 source, Lark 1.2.2, regex 2026.11.15, Windows 11 via ANF Terminal | Three confirmed failing declaration cases before fix, six issue-specific cases after fix, 127 relevant formatter tests passing, toolkit parser and formatting-safety checks; commit 8529a7eb5cfbd0f8433c61b7ca02cf4a7f0eaefa | Godot runtime NOT_RUN. Upstream CI requires maintainer approval; PR open |
| [AcerolaFX PR #64](https://github.com/GarrettGunnell/AcerolaFX/pull/64) | README/Markdown, Git/GitHub CLI, Windows curl.exe redirect checks | Two former gallery links checked as redirects, all seven retained static screenshot paths checked, git diff --check passed; commit 7d9848f34265e3cdb0d6804e5ef284d71c6ecbd3 | Shader/runtime tests NOT_RUN; PR open for upstream review |

**Hardware note:** The cited tests are tooling and file-format checks; GPU, audio hardware, and display configuration were not material to these particular results. No hardware benchmarking is claimed.

## Reusable contribution footnote

Use a short, project-appropriate footer after the technical summary:

> **Specs and evidence:** runtime/tool versions; exact tests and observed results; explicitly unrun checks. **Provenance:** agent-assisted preparation under human-directed oversight, with claims checked against original source and test or CI receipts. Owner and maintainer acceptance are separate.

List exact receipts whenever available. Do not use a previous CI run as proof of a new commit. Do not equate the existence of a PR, a successful mock, or an available runtime with merged, deployed, or accepted behavior.

This page is an evidence index, not a credential, an independent external audit, or a declaration of upstream approval.
