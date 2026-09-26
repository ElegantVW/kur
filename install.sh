#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/bin" "$HOME/.config/systemd/user"
for f in kur kur-server kur_voice.py; do
  cp -f "$ROOT/bin/$f" "$HOME/bin/$f"
  chmod +x "$HOME/bin/$f"
done
cp -f "$ROOT/systemd/kur-server.service" "$HOME/.config/systemd/user/kur-server.service"
echo "kur installed → ~/bin. wake: systemctl --user enable --now kur-server && menagerie ensure kur"
