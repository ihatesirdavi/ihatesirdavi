# Local automation: measured work, not a platform badge

This project showcases local automation executed by the owner-controlled Windows workstation. It is **not ChatGPT scheduled tasks** and **not GitHub Actions**. Cloud-hosted validation is useful for a separate release gate, but it cannot prove that a Windows task executed locally.

## How the current example works

1. **Input:** profile README and supporting public docs, the known public GitHub repositories, and three explicitly named upstream/profile pull requests.
2. **Execution:** Python 3.11 from the Windows workstation, with GitHub public read-only REST requests and local asset validation. No agents, model endpoint, background web server, or cloud runner required.
3. **Receipts:** timestamped JSON snapshots plus an atomic `latest.json` pointer under an owner-selected local directory. Previous snapshots are immutable.
4. **Gate:** distinguish `PASS`, `FAIL` (broken local asset, inaccessible public repository, stale repo redirect, private source), and `UNVERIFIED` (API outage, throttling, or incomplete PR check). Never turn a network error into a false broken-link claim.
5. **Authority:** no API writes, merges, releases, credential extraction, auto-publishing, or change to a second GitHub account. Human owner approval is still required to publish.

Flow:

`Windows Task Scheduler -> local Python -> local assets + public GitHub API -> JSON evidence -> owner review`

## Reproduce the audit locally

From the profile repository on Windows PowerShell:

```powershell
python .\scripts\local_publishing_audit.py --root . --output-dir "$env:LOCALAPPDATA\GitHub-Publishing\Receipts"
python -m unittest discover -s tests -v
```

The script writes no files to the Git repository and does not modify GitHub. No network access is needed for the unit tests because they inject simulated API results. The real audit needs access to public GitHub endpoints, which may be throttled or temporarily unavailable.

The Windows Task Scheduler registration script is [register_local_publishing_audit.ps1](../scripts/register_local_publishing_audit.ps1). It uses the OS scheduler already present on the PC and `pythonw.exe` for a headless run, without creating another scheduler service. Its task is read-only except for local receipts. It must be registered and verified in the owner environment before claiming an active schedule.

## Windows Task Scheduler acceptance (November 20, 2026)

- Existing native OS scheduler, not a new queue, daemon, server, GitHub Action, or ChatGPT task.
- Task: `GitHub-Publishing-Local-Audit`. Daily at **7:30 AM America/New_York**, using the signed-in Windows user context with **limited privileges**, no elevation or UI window. It does not wake or sign in the machine.
- Entrypoint: existing installed Python 3.11 `pythonw.exe` with the audited source and a private output directory selected on the PC.
- Native proof: manually started from Task Scheduler at **07:55:21 ET**; completed with Windows task result **0**, returned to Ready, and wrote a fresh `PASS` JSON receipt at `2026-11-20T12:55:21.743676Z`. No extra persistent `pythonw.exe` process remained.
- This establishes one successful local scheduled execution plus a registered daily trigger. It does not prove a future unattended run has occurred.
- To remove this one local task deliberately: `Unregister-ScheduledTask -TaskName 'GitHub-Publishing-Local-Audit' -Confirm:$false`. No other scheduled tasks are part of its installation.

A `PASS` means the public URLs, known PR metadata requests, and local profile asset checks completed. It does not mean upstream PRs are approved or merged, the entire computer is healthy, or anything has been published.
## What was actually verified

On November 20, 2026, the script ran from the native Windows Python 3.11 environment and returned `PASS`: five public repository references verified, three known pull requests read, zero reported errors. Eight dedicated tests passed; the immutable timestamped file matched the latest receipt. Current receipts also hash the exact README and audit script bytes for source traceability. Local evidence remains on the owner's PC and is **not** uploaded from the machine.

Other existing local scheduled workers can be catalogued as capabilities, but a task showing `Running` in Windows Task Scheduler alone is not proof of successful end-to-end execution. These unrelated services are not automatically part of this public showcase.

## Why it matters

This is a small but inspectable example of automation as engineering, rather than a screenshot of a workflow editor. It combines source inspection, deterministic validation, bounded scheduled execution, failure classification, reproducible evidence, and a release gate. The same habits transfer to testing pipelines, production tooling, and media workflows without falsely claiming those projects are publicly released.