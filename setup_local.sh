#!/usr/bin/env bash
# Bootstrap the IBM Capstone project on macOS / Linux with a compatible Python.
# A Mac's system python3 may be Python 3.9, which cannot install Django >=5.1.
set -euo pipefail
cd "$(dirname "$0")"

if [[ -n "${CAPSTONE_PYTHON:-}" ]]; then
  PYTHON_BIN="$CAPSTONE_PYTHON"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
elif command -v brew >/dev/null 2>&1 && \
     [[ -x "$(brew --prefix python@3.12 2>/dev/null || true)/bin/python3.12" ]]; then
  PYTHON_BIN="$(brew --prefix python@3.12)/bin/python3.12"
else
  PYTHON_BIN="$(command -v python3 || true)"
fi

if [[ -z "${PYTHON_BIN}" ]] || ! "$PYTHON_BIN" -c 'import sys; assert (3,10) <= sys.version_info[:2] < (3,14)' >/dev/null 2>&1; then
  echo "ERROR: Python 3.10–3.13 is required for Django>=5.1; Python 3.12 is recommended." >&2
  echo "On Mac, install with: brew install python@3.12" >&2
  echo 'Then use: CAPSTONE_PYTHON="$(brew --prefix python@3.12)/bin/python3.12" bash setup_local.sh' >&2
  exit 2
fi

SELECTED_VERSION="$($PYTHON_BIN -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
if [[ -d server/.venv ]]; then
  EXISTING_VERSION="$(server/.venv/bin/python -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true)"
  if [[ "$EXISTING_VERSION" != "$SELECTED_VERSION" ]]; then
    echo "Replacing old project virtual environment (Python ${EXISTING_VERSION:-unknown}) with $SELECTED_VERSION"
    rm -rf server/.venv
  fi
fi

echo "Using $($PYTHON_BIN --version) at $PYTHON_BIN"
"$PYTHON_BIN" -m venv server/.venv
source server/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r server/requirements.txt
python -m django --version

export CAPSTONE_DEMO_PASSWORD="${CAPSTONE_DEMO_PASSWORD:-CapstoneDemo2026!}"
export CAPSTONE_ADMIN_PASSWORD="${CAPSTONE_ADMIN_PASSWORD:-CourseAdmin2026!}"
(cd server && python manage.py makemigrations djangoapp --noinput && python manage.py migrate --noinput && python manage.py seed_demo && python manage.py check && python manage.py test djangoapp)

cat <<'MSG'
Setup completed.
Demo user: capstone_demo / CapstoneDemo2026! (unless overridden)
Admin user: root / CourseAdmin2026! (unless overridden)
Collect TEXT evidence: bash collect_all_text.sh
Start app: cd server && source .venv/bin/activate && python manage.py runserver 127.0.0.1:8000
These credentials are for local training only; never use them on a public server.
MSG
