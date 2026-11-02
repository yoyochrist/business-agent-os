#!/bin/sh
set -eu
command -v git >/dev/null || { echo "Install git first"; exit 1; }
command -v python3 >/dev/null || { echo "Install Python 3.11+ first"; exit 1; }
DEST="${HOME}/.local/share/business-agent-os-source"
if [ -d "$DEST/.git" ]; then git -C "$DEST" pull --ff-only
else git clone https://github.com/yoyochrist/business-agent-os.git "$DEST"
fi
exec python3 "$DEST/app.py"
