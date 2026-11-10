#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v gh >/dev/null || { echo 'Install GitHub CLI first'; exit 1; }
run="$(gh run list --workflow=rubric-lint.yml --limit 1 --json databaseId,conclusion --jq '.[] | select(.conclusion=="success") | .databaseId')"
[[ -n "$run" ]] || { echo 'No successful TWO-JOB lint workflow yet. Push .github/workflows/rubric-lint.yml and check Actions.'; exit 1; }
mkdir -p evidence/text
{
 echo "Command: gh run view $run --log"
 echo
 echo "Output from actual completed TWO-JOB GitHub Actions LINT run $run:"
 gh run view "$run" --log
} > evidence/text/CI_CD
echo 'Saved evidence/text/CI_CD'
