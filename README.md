<div align="center">
  <img src="assets/hero.svg" width="100%" alt="Sir Davi. I code sometimes. Function, design, systems and media." />
  <p><strong>I code sometimes. I design, build, test, and make things work.</strong></p>
  <p>
    <a href="#public-previews">Previews</a> ·
    <a href="#featured-public-work">Public work</a> ·
    <a href="#open-source">Open source</a> ·
    <a href="#public-activity">Activity</a> ·
    <a href="#learn-in-public">Lessons</a>
  </p>
</div>

## About

I'm **Sir Davi**, a multidisciplinary creator working across functional design, interactive systems, research, and independent media. The projects come first: what they do, how people use them, and how they feel.

My background includes music production, writing and recording, video editing, and visual design. That creative work informs how I approach engineering: start with the whole system, investigate the mechanics, build a working example, and validate what it really does.

I'm particularly interested in the boundary between low-level systems, AI, graphics, real-time interfaces, and the tools people actually use.

## Where I focus

| Area | What I'm exploring |
| :-- | :-- |
| **Software & systems** | CLI tooling, integrations, desktop/web applications, reliable test and release workflows |
| **Graphics & interactivity** | Shaders, simulation, game technology, real-time rendering, interface animation |
| **Agents & research** | Model tooling, agent workflows, repeatable experiments and applied systems research |
| **Media & production** | Rap/hip-hop, recording, video production, editing, visual storytelling, creative tooling |

## Public previews

**[SIGNAL-001](https://ihatesirdavi.github.io/preview-lab/)** is a small, original interactive visual study of motion, mode switching and bounded playback. The real public prototype is accessible in the browser; its source, checks and release-state contract live in the [Preview Lab repository](https://github.com/ihatesirdavi/preview-lab).

<a href="https://ihatesirdavi.github.io/preview-lab/"><img src="https://raw.githubusercontent.com/ihatesirdavi/preview-lab/main/docs/preview-still.png" width="100%" alt="Real Chrome capture of the SIGNAL-001 prototype interface with a dark procedural field and functional playback controls" /></a>

<sub>Authentic headless Chrome capture, not a mockup. Source tests and the browser-startup smoke passed; complete interaction/visual owner review and packaging remain separate. All unreleased projects use public codenames without revealing private mappings.</sub>
## Featured public work

| Work | What it demonstrates | Current state |
| :-- | :-- | :-- |
| [**SIGNAL-001 / Preview Lab**](https://ihatesirdavi.github.io/preview-lab/) | Original bounded interactive field, three visual modes, tested source and preview evidence | Public prototype; owner acceptance pending |
| [**GitHub profile source**](https://github.com/ihatesirdavi/ihatesirdavi) | Editable SVG design, Python validators, GitHub Actions, and documented lessons | Public and tested |
| [**AcerolaFX contribution**](https://github.com/GarrettGunnell/AcerolaFX/pull/64) | Reproducing broken links, checking evidence, writing a minimal upstream patch | PR #64 submitted for review |
| [**GDScript Toolkit contribution**](https://github.com/Scony/godot-gdscript-toolkit/pull/435) | Python formatter bug fix, regression tests, and semantic checks | PR #435 open; CI approval pending |
| [**VS Code extensions workspace**](https://github.com/ihatesirdavi/vscode-extensions) | Shared extension workspace and provisional visual branding | Public source; release not verified |

Projects in transition are represented by owner-cleared public previews under codenames only. Private names, source and packaging status remain withheld until the owner approves release.

## Tools and creative software

**Software:** Git · GitHub Actions · Python · Go · Rust · TypeScript · Tauri · VS Code

**Graphics and interactive:** Blender · Godot · Adobe creative tools · shader research

**Audio and video:** FL Studio · recording, editing, and digital production workflows

These are tools I use or actively explore, not a claim of equal expertise or published proficiency in each.

## Public activity

<img src="assets/public-activity.svg" width="100%" alt="Graph of recent public GitHub events; not a full contribution calendar" />

<sub>This chart counts recent events from GitHub's public events API only. It is not the platform's full contribution calendar and does not read private repository activity. See the <a href="scripts/render_public_activity.py">generator source</a>.</sub>

## Open source

I prefer **small, reproducible upstream contributions**: verify the issue, check the maintainer's expectations, write an understandable change, test it, and make the PR reviewable.

- [AcerolaFX issue #63](https://github.com/GarrettGunnell/AcerolaFX/issues/63) → [PR #64](https://github.com/GarrettGunnell/AcerolaFX/pull/64): remove broken README gallery links while preserving existing screenshots.
- [GDScript Toolkit issue #394](https://github.com/Scony/godot-gdscript-toolkit/issues/394) -> [PR #435](https://github.com/Scony/godot-gdscript-toolkit/pull/435): preserve warning-annotation newlines and test the result.
- [Explore repositories](https://github.com/ihatesirdavi?tab=repositories) and [pull requests](https://github.com/pulls?q=is%3Apr+author%3Aihatesirdavi) for the current public record.

A submitted pull request is not the same as a merged contribution.

## Learn in public

| Lesson | Learn | Practice |
| :-- | :-- | :-- |
| [**01 · Profile as code**](docs/lessons/01-profile-as-code.md) | Markdown, SVG, Git, local validation | Break an asset link and fix it |
| [**02 · Upstream contribution**](docs/lessons/02-upstream-contribution.md) | Redirects, minimal diffs, branch hygiene | Explain the issue and inspect the PR |
| [**03 · Public activity graphic**](docs/lessons/03-public-activity.md) | Python, dates, APIs, XML, regression testing | Change the time window and test the results |
| [**04 - GDScript formatter bug**](docs/lessons/04-gdscript-formatter.md) | Python, syntax trees, regression tests, and AST safety | Reproduce 3 failures and verify the patch |

## Working method

**Understand → design → practice → validate → explain.**

I care about clean boundaries, honest release status, reusable tools, and understanding *why* a solution works.

---

<sub>**Build and provenance:** Python 3.11, Git/GitHub CLI, GitHub Actions, SVG/XML checks; profile test results and CI are recorded in GitHub Actions. I personally review and double-check the work and its factual claims, with agents assisting implementation, review, and source verification. External maintainer acceptance remains separate. [Specs, test stack, and evidence](docs/contribution-evidence.md).</sub>
