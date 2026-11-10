#!/usr/bin/env bash
# Requires GitHub CLI authenticated as tdao7; creates PUBLIC repo only when user invokes it.
set -euo pipefail
cd "$(dirname "$0")"
command -v gh >/dev/null || { echo 'Install GitHub CLI';exit 1; }
login="$(gh api user --jq .login)"
[[ "$login" == 'tdao7' ]] || { echo "Authenticated as $login, not tdao7";exit 1; }
if [[ ! -d .git ]];then git init -b main;fi
git add .
git diff --cached --quiet || git commit -m 'Complete IBM dealership capstone project with Django API and React registration'
if gh repo view tdao7/ibm-dealership-capstone >/dev/null 2>&1; then
 git remote remove origin 2>/dev/null || true
 git remote add origin https://github.com/tdao7/ibm-dealership-capstone.git
 git push -u origin main
else
 gh repo create tdao7/ibm-dealership-capstone --public --source=. --remote=origin --push
fi
echo 'Public GitHub repository: https://github.com/tdao7/ibm-dealership-capstone'
