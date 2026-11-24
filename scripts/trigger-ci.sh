#!/usr/bin/env bash
# Instant on-demand trigger for ci-worker-01 from any local repo clone.
# Usage: GH_TOKEN=<pat> ./trigger-ci.sh [suite: all|fast|linux|windows]
set -euo pipefail
SUITE="${1:-all}"
SHA="$(git rev-parse HEAD)"
BASE_SHA="$(git rev-parse HEAD~1 2>/dev/null || echo '')"
REF="$(git rev-parse --abbrev-ref HEAD)"
WORKER_REPO="${WORKER_REPO:-pengjiaxusz/ci-worker-01}"

: "${GH_TOKEN:?Please export GH_TOKEN with repo+workflow permissions}"

curl -fsSL -X POST \
  -H "Authorization: Bearer ${GH_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${WORKER_REPO}/dispatches" \
  -d "{\"event_type\":\"run-ci\",\"client_payload\":{\"sha\":\"${SHA}\",\"base_sha\":\"${BASE_SHA}\",\"ref\":\"${REF}\",\"suite\":\"${SUITE}\"}}"

echo "Triggered ${WORKER_REPO} (${SUITE}) for ${REF} @ ${SHA:0:8}"
