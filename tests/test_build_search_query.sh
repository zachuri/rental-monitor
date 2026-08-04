#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$ROOT/scripts/build-search-query.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/area.yml" <<'YAML'
search:
  latitude: 33.739
  longitude: -117.858
  radius: 18
YAML

actual=$($SCRIPT "$TMP/area.yml")
expected='latitude=33.739&longitude=-117.858&radius=18'
if [ "$actual" != "$expected" ]; then
  printf 'FAIL area query\nexpected: %s\nactual:   %s\n' "$expected" "$actual" >&2
  exit 1
fi

printf 'PASS area query\n'

cat > "$TMP/zip.yml" <<'YAML'
zip_code: "92657"
YAML

actual=$($SCRIPT "$TMP/zip.yml")
expected='zipCode=92657'
if [ "$actual" != "$expected" ]; then
  printf 'FAIL ZIP fallback\nexpected: %s\nactual:   %s\n' "$expected" "$actual" >&2
  exit 1
fi

printf 'PASS ZIP fallback\n'
