#!/usr/bin/env sh
set -eu
REPO="https://github.com/yoyochrist/business-agent-os"
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
DOWNLOAD_URL="$REPO/releases/latest/download/$ASSET"
if ! curl -fL "$DOWNLOAD_URL" -o "$INSTALL_DIR/BusinessAgentOS"; then
  echo "No published release found. See $REPO/actions/workflows/build-desktop.yml"
  exit 1
fi
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
