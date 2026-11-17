# Lesson 01: A GitHub profile is a repository

**Goal:** Understand how Markdown, SVG, Git, and automated tests make a developer profile.

## Mechanism
GitHub recognizes a public repository named exactly like its account (here: ihatesirdavi/ihatesirdavi). The root README.md appears on the public profile.

- README.md defines headings, links, badges, and sections.
- assets/hero.svg is an editable vector graphic, not a screenshot.
- scripts/validate_profile.py checks local links and whether SVG parses.
- .github/workflows/validate.yml runs checks for each push and pull request.

GitHub renders Markdown and a restricted set of HTML; a README does not run arbitrary JavaScript.

## Practice: change one thing
1. Add one honest sentence in the README's "What I'm building toward" section.
2. Run: python -m unittest discover -s tests -v
3. Run: python scripts/validate_profile.py
4. Change the color of one circuit path in assets/hero.svg and run the checks again.
5. Explain what changed, what the tests verified, and what still needs visual review.

## Intentionally break something
Change the README banner path to assets/does-not-exist.svg.
Run the validator: it should report the missing file. Revert and confirm the checks pass.

## Explain
- Why must this repository match the GitHub username?
- What does Markdown control versus SVG?
- Why is a passing source test not proof the page renders correctly?
- How does a feature branch make experimentation reversible?
- Why should public source never contain tokens, confidential files, or private URLs?

**Next lesson:** reproduce a real upstream issue, write a minimal fix, test it, and propose a reviewable contribution under the maintainer's rules. Learning is the goal; contribution counts are only a side effect.
