#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${DEPLOYMENT_URL:?Set DEPLOYMENT_URL to an ACTUAL deployed HTTPS address}"
[[ "$DEPLOYMENT_URL" == https://* ]] || { echo 'HTTPS URL required'; exit 1; }
page="$(curl -fL --max-time 25 -sS "$DEPLOYMENT_URL")"
grep -q 'BEST' <<< "$page" || { echo 'Live response does not look like the Best Cars app'; exit 1; }
mkdir -p evidence/text
printf '%s\n' "$DEPLOYMENT_URL" > evidence/text/deploymentURL
echo 'Live deployment verified; saved evidence/text/deploymentURL'
