#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$ROOT/scripts/reserve-api-request.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
LEDGER="$TMP/api-usage.json"

actual=$($SCRIPT "$LEDGER" 2 2026-08)
[ "$actual" = '1/2 requests reserved for 2026-08' ]
[ "$(jq -r '.month' "$LEDGER")" = '2026-08' ]
[ "$(jq -r '.requests' "$LEDGER")" = '1' ]

actual=$($SCRIPT "$LEDGER" 2 2026-08)
[ "$actual" = '2/2 requests reserved for 2026-08' ]

if $SCRIPT "$LEDGER" 2 2026-08 >"$TMP/stdout" 2>"$TMP/stderr"; then
  echo 'FAIL quota should reject request above limit' >&2
  exit 1
fi
[ "$(jq -r '.requests' "$LEDGER")" = '2' ]

actual=$($SCRIPT "$LEDGER" 2 2026-09)
[ "$actual" = '1/2 requests reserved for 2026-09' ]
[ "$(jq -r '.month' "$LEDGER")" = '2026-09' ]
[ "$(jq -r '.requests' "$LEDGER")" = '1' ]

printf 'PASS monthly request quota\n'
