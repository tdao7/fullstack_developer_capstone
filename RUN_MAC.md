# Run the IBM Capstone project on a Mac mini M4

The original error (`No matching distribution found for Django>=5.1` followed by `No module named django`) indicates the active Python is too old. Use Python 3.12 explicitly, not macOS's default `python3`.

## 1. Install Python 3.12, recreate the project environment

Open a Terminal in the extracted `ibm_dealership_capstone` folder:

```bash
cd ~/Downloads/ibm_dealership_capstone
brew install python@3.12
CAPSTONE_PYTHON="$(brew --prefix python@3.12)/bin/python3.12" bash setup_local.sh
```

The updated script replaces the project's old `.venv` if it uses another Python version, installs Django and other requirements, creates/migrates the database, seeds the sample accounts, and runs the project's tests. It does not delete your code or affect other projects.

If Homebrew is missing, install it from https://brew.sh or install Python 3.12 from https://www.python.org/downloads/ and set `CAPSTONE_PYTHON` to the full path of its interpreter.

## 2. Collect the text evidence for the assignment

When setup finishes:

```bash
bash collect_all_text.sh
ls -l evidence/text/
```

The collector briefly runs its own web server on `127.0.0.1:8000`. Do **not** leave another `runserver` running on port 8000 before launching it.

## 3. Run the web application

In Terminal 1:

```bash
cd ~/Downloads/ibm_dealership_capstone
source server/.venv/bin/activate
cd server
python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/ or http://127.0.0.1:8000/admin/ . Local-only demo credentials:

- Demo: `capstone_demo` / `CapstoneDemo2026!`
- Admin: `root` / `CourseAdmin2026!`

## 4. Generate screenshots

In Terminal 2 (keep Terminal 1 running):

```bash
cd ~/Downloads/ibm_dealership_capstone
source server/.venv/bin/activate
python -m pip install -r server/requirements-browser.txt
python -m playwright install chromium
python capture_screenshots.py --base-url http://127.0.0.1:8000
```

Screenshots go in `screenshots/` (the script prints each exact file path). For submissions requiring a visible address bar, capture a screenshot of the whole browser window rather than relying on browser-page screenshots alone. Cloud deployment and GitHub Actions evidence require actually completing those external steps.

## Troubleshooting

```bash
python --version
python -m django --version
which python
```

Expected Python is 3.12.x and Django 5.x. If Python says 3.9.x, the old virtual environment is still active; run `deactivate` then re-run step 1. If `brew` is not found, install Homebrew first. If port 8000 is in use, stop the other Django server with Ctrl+C before collecting text evidence.
