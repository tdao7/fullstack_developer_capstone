#!/usr/bin/env bash
# Collect real API output and a real, SUCCESSFUL Django server-startup transcript.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
source server/.venv/bin/activate
export CAPSTONE_DEMO_PASSWORD="${CAPSTONE_DEMO_PASSWORD:-CapstoneDemo2026!}"
export CAPSTONE_ADMIN_PASSWORD="${CAPSTONE_ADMIN_PASSWORD:-CourseAdmin2026!}"
mkdir -p evidence/text

# A truly free listener port. Avoid recording a port-conflict as successful evidence.
PORT="$(python - <<'PY'
import socket
with socket.socket() as s:
 s.bind(('127.0.0.1',0))
 print(s.getsockname()[1])
PY
)"
BASE="http://127.0.0.1:$PORT"
(cd server && python manage.py makemigrations djangoapp --noinput && python manage.py migrate --noinput && python manage.py seed_demo >/dev/null)
LOG="$ROOT/evidence/text/django_server.log"
(
 cd server
 exec python -u manage.py runserver "127.0.0.1:$PORT" --noreload
) > "$LOG" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
ready=0
for _ in $(seq 1 80); do
 if curl --max-time 2 -fsS "$BASE/djangoapp/get_dealers" >/dev/null 2>&1; then ready=1;break;fi
 if ! kill -0 "$SERVER_PID" 2>/dev/null;then break;fi
 sleep .5
done
if [[ "$ready" != 1 ]];then echo "Django failed to start. Full log:";cat "$LOG";exit 1;fi
sleep 1
if ! grep -q 'Starting development server at' "$LOG"; then
 echo "Missing successful start marker" >&2;cat "$LOG";exit 1
fi
if grep -q 'port is already in use' "$LOG"; then
 echo "The server log contains a port conflict; refusing to submit as success." >&2;exit 1
fi
printf 'Command: cd server && python manage.py runserver 127.0.0.1:%s --noreload\n\nOutput:\n\n' "$PORT" > evidence/text/django_server
cat "$LOG" >> evidence/text/django_server
printf '\nSuccessfully started on %s\n' "$BASE"

record() {
 local name="$1";local path="$2";shift 2
 local response
 response="$(curl -fsS --max-time 15 "$@" "$BASE$path")"
 printf 'Command: curl -sS %s\n\nOutput:\n\n%s\n' "$BASE$path" "$response" > "evidence/text/$name"
 printf '%s: %s\n' "$name" "${response:0:450}"
}
# Authentication: keep session cookie. Mask password in evidence command line.
login="$(curl -fsS --max-time 15 -c evidence/session.cookie -H 'Content-Type: application/json' -X POST -d "{\"userName\":\"capstone_demo\",\"password\":\"$CAPSTONE_DEMO_PASSWORD\"}" "$BASE/djangoapp/login")"
printf 'Command: curl -sS -c session.cookie -X POST %s/djangoapp/login -H "Content-Type: application/json" -d '\''{"userName":"capstone_demo","password":"********"}'\''\n\nOutput:\n\n%s\n' "$BASE" "$login" > evidence/text/loginuser
logout="$(curl -fsS --max-time 15 -b evidence/session.cookie "$BASE/djangoapp/logout")"
printf 'Command: curl -sS -b session.cookie %s/djangoapp/logout\n\nOutput:\n\n%s\n' "$BASE" "$logout" > evidence/text/logoutuser
python - "$login" "$logout" <<'PY'
import json,sys
assert json.loads(sys.argv[1])['status']=='Authenticated'
assert json.loads(sys.argv[2])=={'userName':'','status':'Logged out'}
PY
record getdealerreviews /djangoapp/reviews/dealer/1
record getalldealers /djangoapp/get_dealers
record getdealerbyid /djangoapp/dealer/1
record getdealersbyState /djangoapp/get_dealers/Kansas
record getallcarmakes /djangoapp/get_cars
python - "$BASE" <<'PY'
import urllib.request,json,sys
base=sys.argv[1]
def get(path):return json.load(urllib.request.urlopen(base+path))
dealers=get('/djangoapp/get_dealers')['dealers']
if len(dealers)!=50:
 raise SystemExit(f'Q9 NOT READY: found {len(dealers)} dealers instead of 50. Run bash refresh_official_data.sh FIRST.')
assert all('purchase_date' in r for r in get('/djangoapp/reviews/dealer/1')['reviews'])
assert all(set(('CarModel','CarMake')).issubset(r) for r in get('/djangoapp/get_cars')['CarModels'])
print('Verified Q8/Q9/Q14 rubric format and 50 official dealer records.')
PY
record analyzereview /djangoapp/analyze/Fantastic%20services
# Q15 command points to in-process Django sentiment endpoint; valid actual result, no 5050 collision.
rm -f evidence/session.cookie
printf '\nSaved real text evidence in evidence/text.\n'
