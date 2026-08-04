#!/usr/bin/env bash
set -euo pipefail

LEDGER=${1:-data/api-usage.json}
MAX_REQUESTS=${2:-50}
MONTH=${3:-$(date -u +%Y-%m)}

if ! [[ "$MAX_REQUESTS" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: monthly request limit must be a positive integer" >&2
  exit 2
fi

mkdir -p "$(dirname "$LEDGER")"

if [ -f "$LEDGER" ]; then
  if ! jq -e 'type == "object" and (.month | type == "string") and (.requests | type == "number" and floor == . and . >= 0)' "$LEDGER" >/dev/null; then
    echo "ERROR: refusing API request because $LEDGER is invalid" >&2
    exit 2
  fi
  ledger_month=$(jq -r '.month' "$LEDGER")
  requests=$(jq -r '.requests' "$LEDGER")
else
  ledger_month="$MONTH"
  requests=0
fi

if [ "$ledger_month" != "$MONTH" ]; then
  ledger_month="$MONTH"
  requests=0
fi

if [ "$requests" -ge "$MAX_REQUESTS" ]; then
  echo "ERROR: monthly RentCast request limit reached ($requests/$MAX_REQUESTS for $MONTH)" >&2
  exit 3
fi

requests=$((requests + 1))
tmp=$(mktemp "${LEDGER}.XXXXXX")
trap 'rm -f "$tmp"' EXIT
jq -n --arg month "$ledger_month" --argjson requests "$requests" \
  '{month: $month, requests: $requests}' > "$tmp"
mv "$tmp" "$LEDGER"
trap - EXIT

printf '%s/%s requests reserved for %s\n' "$requests" "$MAX_REQUESTS" "$MONTH"
