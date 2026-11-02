# Business Agent OS

Local-first business agent starter, controlled from a browser, Claude Code, Codex or Antigravity skill instructions.

**Status:** prototype, not yet a complete A2A/Graphify service or native installer. Draft-only: no autonomous email sending, publishing or payments. Task API requests require a per-run random token; CLI prompts are passed through standard input rather than command-line arguments.

## One-command installation

### macOS (Terminal)

Open **Terminal**, paste this command and press Return:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/yoyochrist/business-agent-os/main/install.sh)"
```

Once installed, launch Business Agent OS with:

```bash
~/.local/bin/business-agent-os
```

The dashboard opens at http://127.0.0.1:8765.

**macOS requirements:** A published [macOS GitHub Release](https://github.com/yoyochrist/business-agent-os/releases) must exist, and the executable is currently unsigned/not notarized, so macOS may block it. The app reuses an officially installed and signed-in Codex or Claude Code CLI; it cannot sign in to either service on your behalf.

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/yoyochrist/business-agent-os/main/install.ps1 | iex
```

### Linux (Terminal)

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/yoyochrist/business-agent-os/main/install.sh)"
```

**Before installing:** Review the [macOS/Linux installer script](install.sh) or [Windows installer script](install.ps1). These commands download published GitHub Release binaries, not credentials. If a release is not yet published, the installer provides the [desktop build workflow](https://github.com/yoyochrist/business-agent-os/actions/workflows/build-desktop.yml); the installation will not finish automatically.

For alternatives and troubleshooting, read [INSTALL.md](INSTALL.md).

## Easy installation (no Python required)

Read [INSTALL.md](INSTALL.md), then download a built executable from the [Desktop Builds workflow](https://github.com/yoyochrist/business-agent-os/actions/workflows/build-desktop.yml). Extract and double-click the executable. Downloads only appear after a successful build.

You still need an officially installed and signed-in Codex CLI or Claude Code CLI to execute AI tasks.

## Developer installation
1. Install Python 3.11+.
2. Install the official **Codex CLI** or **Claude Code CLI** and sign in through its own normal login flow.
3. Download this repository.
4. On Windows, double-click `Start-Windows.bat`; on macOS/Linux run `sh Start-Mac-Linux.command`.
5. Open http://127.0.0.1:8765 and choose an agent.

The application calls the official CLI executable using the credentials it already manages. **It never reads, copies, or extracts credential files.** No provider API key or provider Python SDK is required.

## Roles
PM, HR, Accountant, Finance, Sales, Marketing plus Business Orchestrator, Knowledge, and Approvals.

## Integration boundaries
- **Codex:** official `codex exec` CLI for draft tasks, with skills in `.agents/skills`.
- **Claude Code:** official `claude -p` CLI for draft tasks, with skills in `.claude/skills`.
- **Antigravity:** editor-side skills in `.agents/skills`. Its sign-in is **not** a supported headless inference backend.
- **Knowledge:** SQLite task history only; Graphify indexing and PostgreSQL graph are future milestones.
- **Email and messaging:** no external sending currently implemented.
- **A2A/MCP:** specified as planned architecture, not yet operational.

## First release: maintainer checklist

The terminal installers require a published GitHub Release. The connected GitHub integration cannot publish one automatically. To publish the first release:

1. Open [Draft a new release](https://github.com/yoyochrist/business-agent-os/releases/new).
2. Create tag `v0.1.0` targeting `main`, then publish.
3. The `release.published` workflow will build Windows, macOS and Linux binaries and attempt to attach them to the release.
4. Check the [Build desktop downloads workflow](https://github.com/yoyochrist/business-agent-os/actions/workflows/build-desktop.yml) and confirm all three release assets are attached before recommending the one-line installers.

**Security note:** Session tokens are randomly generated on startup, carried in the browser URL fragment and then removed from the address bar. Do not share an active session link or use this prototype on a shared machine for sensitive client information. No persistent user accounts or OS-level access controls exist. Executables are currently unsigned; Windows SmartScreen and macOS Gatekeeper may warn.

## Tests

```bash
python -m unittest discover -s tests
```

## Roadmap
1. Local authentication and robust single-instance dashboard
2. Persistent A2A task service and agent registry
3. MCP gateway for editor clients
4. Graphify document indexing and scoped business knowledge retrieval
5. Inbox/communication hooks with human approval and audit trail
6. Signed installers for non-technical users

## Signed desktop releases

Current desktop artifacts are unsigned and may trigger Windows SmartScreen or macOS Gatekeeper. See [SIGNING.md](SIGNING.md) for the verified publisher identity, Windows code signing, macOS Developer ID/notarization, and release verification process. Until those credentials and CI steps are configured, treat packages as **unsigned previews** rather than warning-free production installers.

## Safety
Do not expose the local server to the public Internet. Do not run tasks with untrusted local credentials. Any future provider/connection must use official authentication methods only.
