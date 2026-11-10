#!/usr/bin/env bash
# Fetch the official IBM lab dataset (50 dealership rows). Save actual source file, not mock data.
set -euo pipefail
cd "$(dirname "$0")"
URL='https://raw.githubusercontent.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone/main/server/database/data/dealerships.json'
DST='server/djangoapp/official_dealerships.json'
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
curl -fLSs --retry 3 --connect-timeout 12 "$URL" -o "$TMP"
python3 - "$TMP" <<'VERIFY'
import json,sys
with open(sys.argv[1],encoding='utf-8') as f: data=json.load(f)
assert len(data['dealerships'])==50, 'Expected 50 dealer rows in IBM course dataset'
assert any(d['state']=='Kansas' for d in data['dealerships']), 'Expected Kansas sample'
print(f"Verified official course dataset: {len(data['dealerships'])} dealerships")
VERIFY
mv "$TMP" "$DST"
echo "Saved $DST (commit this file for CI and cloud environments)"
