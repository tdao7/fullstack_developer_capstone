#!/usr/bin/env bash
# Collect actual Django/API outputs after local setup. Does NOT invent CI or deployment results.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/evidence/text"
printf "%s\n\n%s\n" "Command: cd server && python manage.py runserver 127.0.0.1:8000 --noreload" "Output:" > "$ROOT/evidence/text/django_server"
cd "$ROOT"
source server/.venv/bin/activate
export CAPSTONE_DEMO_PASSWORD="${CAPSTONE_DEMO_PASSWORD:-CapstoneDemo2026!}"
export CAPSTONE_ADMIN_PASSWORD="${CAPSTONE_ADMIN_PASSWORD:-CourseAdmin2026!}"
(cd server && python manage.py makemigrations djangoapp --noinput && python manage.py migrate --noinput && python manage.py seed_demo >/dev/null)
(
 cd server
 PYTHONUNBUFFERED=1 python manage.py runserver 127.0.0.1:8000 --noreload 2>&1
) >> "$ROOT/evidence/text/django_server" &
SERVER_PID=$!
(python -u server/sentiment_service.py) > "$ROOT/evidence/text/sentiment_server" 2>&1 &
SENTIMENT_PID=$!
trap 'kill "$SERVER_PID" "$SENTIMENT_PID" 2>/dev/null || true' EXIT
for _ in $(seq 1 45); do
 if curl -fsS 'http://127.0.0.1:8000/djangoapp/get_dealers' >/dev/null;then break;fi
 sleep 1
done
curl -fsS 'http://127.0.0.1:8000/djangoapp/get_dealers' >/dev/null
sleep 1
record(){ local output="$1";local cmd="$2";shift 2
 local response;response="$(curl -sS "$@")"
 printf '%s\n\n%s\n\n%s\n' "Command: $cmd" "Output:" "$response" > "$ROOT/evidence/text/$output"
 printf '%s: %s\n' "$output" "$response"
}
record loginuser 'curl -sS -c session.cookie -X POST http://127.0.0.1:8000/djangoapp/login -H "Content-Type: application/json" -d '\''{"userName":"capstone_demo","password":"********"}'\''' -c "$ROOT/evidence/session.cookie" -X POST 'http://127.0.0.1:8000/djangoapp/login' -H 'Content-Type: application/json' -d "{\"userName\":\"capstone_demo\",\"password\":\"$CAPSTONE_DEMO_PASSWORD\"}"
record logoutuser 'curl -sS -b session.cookie http://127.0.0.1:8000/djangoapp/logout' -b "$ROOT/evidence/session.cookie" 'http://127.0.0.1:8000/djangoapp/logout'
record getdealerreviews 'curl -sS http://127.0.0.1:8000/djangoapp/reviews/dealer/1' 'http://127.0.0.1:8000/djangoapp/reviews/dealer/1'
record getalldealers 'curl -sS http://127.0.0.1:8000/djangoapp/get_dealers' 'http://127.0.0.1:8000/djangoapp/get_dealers'
record getdealerbyid 'curl -sS http://127.0.0.1:8000/djangoapp/dealer/1' 'http://127.0.0.1:8000/djangoapp/dealer/1'
record getdealersbyState 'curl -sS http://127.0.0.1:8000/djangoapp/get_dealers/Kansas' 'http://127.0.0.1:8000/djangoapp/get_dealers/Kansas'
record getallcarmakes 'curl -sS http://127.0.0.1:8000/djangoapp/get_cars' 'http://127.0.0.1:8000/djangoapp/get_cars'
record analyzereview 'curl -sS http://127.0.0.1:5050/analyze/Fantastic%20services' 'http://127.0.0.1:5050/analyze/Fantastic%20services'
rm -f "$ROOT/evidence/session.cookie"
cat <<'MSG'
All local text evidence files saved to evidence/text.
Q22 CI_CD is created ONLY after a real successful GitHub Actions workflow.
Q23 deploymentURL is created ONLY after an actual accessible public deployment.
MSG
