#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

output=$(./simulate.sh data/fixtures/oc-sample-response.json)

if [[ "$output" != *'after street + price filter: 2'* ]]; then
  printf 'FAIL expected two qualifying OC fixtures\n%s\n' "$output" >&2
  exit 1
fi

if [[ "$output" != *'oc-fixture-002-over-cap'* ]]; then
  printf 'FAIL expected the over-cap fixture to be excluded\n%s\n' "$output" >&2
  exit 1
fi

printf 'PASS area-wide price filtering\n'
