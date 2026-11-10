#!/usr/bin/env bash
# Run from repository root. Requires installed Django dependencies.
set -euo pipefail
cd "$(dirname "$0")"
source server/.venv/bin/activate
cd server
python manage.py migrate --noinput
python manage.py shell -c "from django.contrib.auth.models import User; u,created=User.objects.get_or_create(username='capstone_demo',defaults={'email':'demo@example.com'}); u.set_password('CapstoneDemo2026!'); u.save(); print('Demo user is ready')"
PYTHONUNBUFFERED=1 python manage.py runserver 127.0.0.1:8000 --noreload > ../django_server 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
for i in $(seq 1 30); do
  if curl --silent --fail http://127.0.0.1:8000/djangoapp/get_dealers >/dev/null; then break; fi
  sleep 1
done
curl --silent --fail http://127.0.0.1:8000/djangoapp/get_dealers > /dev/null
cd ..
curl -sS -c session.cookie -X POST 'http://127.0.0.1:8000/djangoapp/login' -H 'Content-Type: application/json' -d '{"userName":"capstone_demo","password":"CapstoneDemo2026!"}' > loginuser.response
printf '%s\n%s\n\n%s\n' 'curl -sS -c session.cookie -X POST http://127.0.0.1:8000/djangoapp/login -H "Content-Type: application/json" -d '\''{"userName":"capstone_demo","password":"CapstoneDemo2026!"}'\''' 'Output:' "$(cat loginuser.response)" > loginuser
curl -sS -b session.cookie 'http://127.0.0.1:8000/djangoapp/logout' > logoutuser.response
printf '%s\n%s\n\n%s\n' 'curl -sS -b session.cookie http://127.0.0.1:8000/djangoapp/logout' 'Output:' "$(cat logoutuser.response)" > logoutuser
curl -sS 'http://127.0.0.1:8000/djangoapp/reviews/dealer/1' > getdealerreviews.response
printf '%s\n%s\n\n%s\n' 'curl -sS http://127.0.0.1:8000/djangoapp/reviews/dealer/1' 'Output:' "$(cat getdealerreviews.response)" > getdealerreviews
curl -sS 'http://127.0.0.1:8000/djangoapp/get_dealers' > getalldealers.response
printf '%s\n%s\n\n%s\n' 'curl -sS http://127.0.0.1:8000/djangoapp/get_dealers' 'Output:' "$(cat getalldealers.response)" > getalldealers
curl -sS 'http://127.0.0.1:8000/djangoapp/dealer/1' > getdealerbyid.response
printf '%s\n%s\n\n%s\n' 'curl -sS http://127.0.0.1:8000/djangoapp/dealer/1' 'Output:' "$(cat getdealerbyid.response)" > getdealerbyid
rm -f *.response session.cookie
printf '\nSaved actual test outputs to:\n'
printf ' - %s\n' django_server loginuser logoutuser getdealerreviews getalldealers getdealerbyid
