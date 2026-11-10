#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v gh >/dev/null || { echo 'Install GitHub CLI first'; exit 1; }
run="$(gh run list --workflow=django-ci.yml --limit 1 --json databaseId,conclusion --jq '.[] | select(.conclusion=="success") | .databaseId')"
[[ -n "$run" ]] || { echo 'No successful Django CI run yet. Push to GitHub and check Actions.'; exit 1; }
mkdir -p evidence/text
{
 echo "Command: gh run view $run --log"
 echo
 echo "Output from actual completed GitHub Actions run $run:"
 gh run view "$run" --log
} > evidence/text/CI_CD
echo 'Saved evidence/text/CI_CD'
