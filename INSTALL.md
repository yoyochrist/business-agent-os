# Install Business Agent OS (no Python needed)

## Windows
1. Open the [Actions page](https://github.com/yoyochrist/business-agent-os/actions/workflows/build-desktop.yml).
2. Select the latest **successful** run of **Build desktop downloads**.
3. Download `BusinessAgentOS-Windows` from its Artifacts section (GitHub login may be required).
4. Extract the ZIP and double-click `BusinessAgentOS.exe`.
5. Your browser opens at **http://127.0.0.1:8765**.

## macOS
Download the `BusinessAgentOS-macOS` artifact, extract it, and run the included executable. This prototype is **not code-signed or notarized**, so macOS Gatekeeper may block it. Do not bypass operating-system protections unless you explicitly trust the source and build.

## Linux
Download `BusinessAgentOS-Linux`, extract, mark the binary executable (`chmod +x BusinessAgentOS`) and run it.

## First-run checklist
- The application itself needs no Python installation when using the packaged downloads.
- **AI execution still requires either Codex CLI or Claude Code CLI**, installed separately and already signed in through the official command-line login.
- Choose Codex or Claude Code and enter a draft task.
- It does **not** use Antigravity's credentials for model calls.
- No email or message is sent automatically.

## Troubleshooting
- **CLI not installed**: use the official Codex or Claude Code installation guide and complete its sign-in process first.
- **Browser did not open**: go to http://127.0.0.1:8765 while the app is running.
- **Port already used**: close the other Business Agent OS instance.
- **Security warning**: unsigned prototype executables may be blocked by Windows SmartScreen or macOS Gatekeeper. Verify the build source before trusting it.
- **Task appears stuck**: CLI login might need attention. Open your CLI separately and verify the sign-in.

## Security and limitations
- The app listens only on the local loopback interface.
- Task history is stored in `~/.business-agent-os/tasks.db`.
- Your prompts are sent to the selected CLI's configured model provider under that CLI's normal authentication and policy.
- No Graphify, A2A routing, MCP gateway, or external email/messaging integrations are operational yet.
- The workflow generates **portable unsigned executables**, not OS-native signed installers. GitHub Actions builds must succeed before downloads exist.
