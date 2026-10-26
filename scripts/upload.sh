#!/bin/bash
# Adds files to the `media` branch (keeps the files already there, so earlier
# scheduled posts that point at them keep working) and prints their raw URLs.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
URL="$(git -C "$REPO" remote get-url origin)"
FILES=()
for f in "$@"; do FILES+=("$(realpath "$f")"); done
TMP="$(mktemp -d)"
if git clone -q --depth 1 --branch media "$URL" "$TMP" 2>/dev/null; then
  cd "$TMP"
else
  cd "$TMP"; git init -q; git checkout -q -b media
fi
for f in "${FILES[@]}"; do cp "$f" "$TMP/"; done
git add -A
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -qm "media upload"
git push -q "$URL" media
for f in "${FILES[@]}"; do echo "https://raw.githubusercontent.com/Kosyanvag/channel-media/media/$(basename "$f")"; done
