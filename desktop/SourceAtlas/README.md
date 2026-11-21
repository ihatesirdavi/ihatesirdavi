# Source Atlas (native Windows research and publishing)

Source Atlas is an owner-local, session-resident Windows viewer and research monitor. It extends the existing GitHub profile/publishing audit; it is not a cloud agent, Windows service, external scheduler, GitHub Actions replacement, or automated social engagement bot.

## How it operates

- A single WinForms (.NET 9 Windows Desktop) process uses a named Windows mutex. Launching the desktop shortcut again sends a native activation message and reveals the existing window rather than opening another process.
- The Windows Startup shortcut begins in the tray without stealing focus. Closing the window hides it; the tray menu provides Open, Run audit now, Pause/Resume, and Exit.
- The resident process watches only research roots explicitly enumerated in an owner-private configuration. Relevant source files trigger debounced scans, with a minimum quiet period and a deferred retry if a change arrives too soon. Public profile/repository checks also occur every 15 minutes while the process is running.
- Each scan invokes the **existing, hash-verified local Python audit bundle** without opening a terminal. Original immutable JSON evidence and an atomic latest.json pointer remain the data contract; live-state heartbeat data is local and does not contain raw note bodies or private source paths.
- The interface separates public reference discovery, dated GitHub repository validation, historical engagement, and local evidence. The full 192-repository external verification is a historical snapshot, **not a 15-minute live recheck of all upstreams**.
- The existing physical-monitor role resolver selects the user's chosen LG or agent TCL screen by monitor identity, not by transient Windows DISPLAYn numbering. Native Windows UI scaling is per-monitor; the full three-screen hardware acceptance is not implied by simulated sizes.

## Safety and ownership

- Github engagements (stars, follows, forks, issue reactions), credentials, repository modifications, pull-request merges, and publication are **not actions of the live monitor**.
- Research citation is not endorsement, installation, license permission, or owner approval. GitHub statuses, research candidate metadata, and test receipts have separate provenance and freshness.
- The resident agent stops at Windows sign-out. The per-user Startup shortcut relaunches at the next interactive sign-in; a real reboot/login acceptance has not yet been observed. No service, watchdog, or second task is registered.
- The previous daily Windows Task Scheduler registration was disabled only after installed resident monitoring passed a live test. It is preserved with its original action/trigger state for rollback. No settings outside this workstream are changed.
- Original private output directories and machine-specific paths are intentionally excluded from version control. The source assumes the already-installed local audit bundle and Python runtime; distribution requires explicit installation/configuration.

## Source and test entry points

- Native .NET: SourceAtlas.csproj, Program.cs, DashboardForm.cs, AuditSnapshot.cs, LiveRunPolicy.cs, LiveResearchMonitor.cs.
- Existing read-only audit: ../../scripts/local_publishing_audit.py and ../../scripts/research_public_sources.py.
- Offline Python regressions: ../../tests/test_local_publishing_audit.py and ../../tests/test_research_public_sources.py.
- Build on Windows: run dotnet build desktop/SourceAtlas/SourceAtlas.csproj -c Release.
- SourceAtlas.exe --self-test --evidence output.json executes offline native fixture/policy checks without starting a UI or background monitor. The normal GUI needs explicit --data, --resolver, --root and --role flags. Only the per-user Startup shortcut adds --start-hidden.
- Native qualification for the current owner session includes real Windows 40-inch TCL placement, a nonblank installed-window screenshot, a source-file watcher end-to-end audit, close-to-tray heartbeat, login-shortcut invocation, and a second activation of the same process. None of these alone proves owner visual acceptance or reboot survival.

This code is an inspectable candidate until owner-reviewed and accepted. Original machine evidence stays on the owner workstation and is not copied into this public repository.
