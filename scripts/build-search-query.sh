#!/usr/bin/env bash
set -euo pipefail

CONFIG=${1:-monitor-config.yml}

latitude=$(yq '.search.latitude // ""' "$CONFIG")
longitude=$(yq '.search.longitude // ""' "$CONFIG")
radius=$(yq '.search.radius // ""' "$CONFIG")

if [ -n "$latitude" ] || [ -n "$longitude" ] || [ -n "$radius" ]; then
  if [ -z "$latitude" ] || [ -z "$longitude" ] || [ -z "$radius" ]; then
    echo 'ERROR: area search requires search.latitude, search.longitude, and search.radius' >&2
    exit 1
  fi
  printf 'latitude=%s&longitude=%s&radius=%s\n' "$latitude" "$longitude" "$radius"
  exit 0
fi

zip_code=$(yq '.zip_code // ""' "$CONFIG")
if [ -z "$zip_code" ]; then
  echo 'ERROR: configure an area search or zip_code' >&2
  exit 1
fi

printf 'zipCode=%s\n' "$zip_code"
