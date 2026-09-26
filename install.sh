#!/usr/bin/env bash
# kur install — bins + unit. Kur needs a mind (menagerie, port 8081);
# without it the pen stays asleep. See DEPS below.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/bin" "$HOME/.config/systemd/user"
for f in kur kur-server kur_voice.py; do
  cp -f "$ROOT/bin/$f" "$HOME/bin/$f"
  chmod +x "$HOME/bin/$f"
done
cp -f "$ROOT/systemd/kur-server.service" "$HOME/.config/systemd/user/kur-server.service"

# DEPS: menagerie (model host on :8081). Without it the pen stays asleep.
if [[ "${1:-}" == "--with-menagerie" ]]; then
  if [[ ! -x "$HOME/bin/menagerie" ]]; then
    echo "kur: fetching the mind (ElegantVW/pixie for menagerie)…"
    if [[ ! -d "$HOME/pixie" ]]; then
      git clone git@github.com:ElegantVW/pixie.git "$HOME/pixie"
    fi
    (cd "$HOME/pixie" && ./install.sh)
  fi
elif [[ ! -x "$HOME/bin/menagerie" ]]; then
  echo "kur: WARNING — no menagerie on PATH; the mind (:8081) is missing." >&2
  echo "kur:   next:  ./install.sh --with-menagerie" >&2
  echo "kur:   or:    git clone git@github.com:ElegantVW/pixie.git ~/pixie && cd ~/pixie && ./install.sh" >&2
fi
echo "kur installed → ~/bin. wake: systemctl --user enable --now kur-server && menagerie ensure kur"
