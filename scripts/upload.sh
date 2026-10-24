#!/bin/bash
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
URL="$(git -C "$REPO" remote get-url origin)"
TMP="$(mktemp -d)"
cd "$TMP"
git init -q
git checkout -q -b media
for f in "$@"; do cp "$f" "$TMP/"; done
git add -A
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -qm "media upload"
git push -q --force "$URL" media
for f in "$@"; do echo "https://raw.githubusercontent.com/Kosyanvag/channel-media/media/$(basename "$f")"; done
