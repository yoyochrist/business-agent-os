#!/usr/bin/env sh
set -eu
REPO="https://github.com/yoyochrist/business-agent-os"
API="https://api.github.com/repos/yoyochrist/business-agent-os/releases/latest"
OS="$(uname -s)"
case "$OS" in
  Darwin) ASSET="BusinessAgentOS-macOS" ;;
  Linux) ASSET="BusinessAgentOS-Linux" ;;
  *) echo "Unsupported OS: $OS"; exit 1 ;;
esac
command -v curl >/dev/null 2>&1 || { echo "curl is required"; exit 1; }
INSTALL_DIR="${HOME}/.local/share/business-agent-os"
mkdir -p "$INSTALL_DIR" "${HOME}/.local/bin"
echo "Looking for the latest GitHub release..."
DOWNLOAD_URL="$(curl -fsSL "$API" | python3 -c 'import json,sys; d=json.load(sys.stdin); a=next((x for x in d.get("assets",[]) if x.get("name")==sys.argv[1]),None); print(a["browser_download_url"] if a else "")' "$ASSET" 2>/dev/null || true)"
if [ -z "$DOWNLOAD_URL" ]; then
  echo "No published desktop release with $ASSET yet."
  echo "Builds: $REPO/actions/workflows/build-desktop.yml"
  exit 1
fi
curl -fL "$DOWNLOAD_URL" -o "$INSTALL_DIR/BusinessAgentOS"
chmod 700 "$INSTALL_DIR/BusinessAgentOS"
cat > "$HOME/.local/bin/business-agent-os" <<EOF
#!/bin/sh
exec "$INSTALL_DIR/BusinessAgentOS" "\$@"
EOF
chmod 700 "$HOME/.local/bin/business-agent-os"
echo "Installed. Run: $HOME/.local/bin/business-agent-os"
if ! command -v codex >/dev/null 2>&1 && ! command -v claude >/dev/null 2>&1; then
  echo "Install and sign in to Codex CLI or Claude Code CLI for AI tasks."
fi
