#!/usr/bin/env bash
set -euo pipefail

REMOTE="norm@178.156.201.237"
REMOTE_DIR="/home/norm/gpt-sportswriter-discord"
REMOTE_SERVICE="gpt-sportswriter-discord.service"
BRANCH="main"
INSTALL_DEPS="${INSTALL_DEPS:-0}"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing to deploy: local repo has uncommitted changes." >&2
  git status --short >&2
  exit 1
fi

echo "Pushing ${BRANCH} to origin..."
git push origin "$BRANCH"

echo "Refreshing VPS checkout and restarting Discord bot..."
ssh "$REMOTE" env INSTALL_DEPS="$INSTALL_DEPS" bash <<'EOSSH'
set -euo pipefail
REMOTE_DIR="/home/norm/gpt-sportswriter-discord"
REMOTE_SERVICE="gpt-sportswriter-discord.service"
BRANCH="main"

cd "$REMOTE_DIR"
git fetch origin
git reset --hard "origin/${BRANCH}"

if [[ "$INSTALL_DEPS" == "1" ]]; then
  .venv/bin/pip install -r requirements.txt
fi

sudo systemctl restart "$REMOTE_SERVICE"
sleep 3
sudo systemctl is-active --quiet "$REMOTE_SERVICE"
systemctl status "$REMOTE_SERVICE" --no-pager -l | sed -n '1,20p'
EOSSH

echo "Discord bot deploy complete."
