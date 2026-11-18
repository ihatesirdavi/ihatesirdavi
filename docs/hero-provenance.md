# Profile banner source and review

**Update:** November 18, 2026. Public design candidate; owner visual review pending.

## The actual composition

The previous iteration placed two screenshots side by side. The present revision corrects that mistake. It renders **one unified field** combining music arrangement, synthetic waveform, signal routing and mathematically simulated gravitational paths. There are no screenshot panels, embedded preview images or unpublished source assets.

The static PNG and finite GIF are produced by scripts/render_music_hero.py (Python and Pillow). The profile uses the same asset names to avoid breaking its public banner link. The original SVG was superseded previously.

The original algorithmic study **SIGNAL-001** inspired the procedural signal and visual-mode concepts, while the existing public educational **DYNAMICS-002** inspired the softened three-body velocity Verlet model and orbital paths. This does not reproduce their interfaces or imply that they are installed or released products. The audio signal is **synthetic**, not the owner's copyrighted recording or a claim of an actual DAW waveform.

## Design and motion

The color direction is informed by the owner's provisional Sir Davi design reference: deep charcoal, off-white lettering, muted mauve and copper. Signal routing transitions gradually from warm audio elements through processing nodes to restrained cooler trajectories. Arrangement lanes, nodes and gravitational paths are built from original geometry in one canvas, not cards or screenshots.

The original Sir Davi logo/wordmark was referenced in creator notes but is not present as a verified, publishable original logo asset. The displayed text treatment is not a fabricated logo. Logo integration requires a verified owner-provided export.

The GitHub banner's PNG is 1600 x 470. The GIF contains 18 frames with 140ms per frame and a finite two-cycle animation before it stops. The motion animates the synthetic signal and orbital highlights; there is no perpetual playback. GitHub determines actual playback and caching behavior.

## Reproduce and evidence

    python scripts/render_music_hero.py
    python -m unittest discover -s tests -v
    python scripts/validate_profile.py

Source environment: Windows 11, Python 3.11, Pillow 11.1.0. Fonts resolve to local installed system fonts and are not distributed. Cross-machine pixel fidelity may differ due to fonts or rasterization, but design intent and generated-asset checks are source-inspectable.

**Review pending:** These tests prove source reproducibility, bounded asset structure and finite motion, not owner aesthetic acceptance. The banner is not a private software package and does not authorize disclosure of private project names.