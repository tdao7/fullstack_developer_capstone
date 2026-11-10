# IBM Capstone — resubmission guide after 24/50 result

This project kit addresses the grader feedback. It does NOT include fabricated screenshots or a pretend successful Code Engine deployment. Your actual URLs/screenshots must be generated from a running deployment.

## Before running anything

**Backup your existing project**. Extract this ZIP into its own new directory. Python 3.12 virtualenv and DB are not included.

Run:

```bash
cd ~/Downloads/ibm_capstone_rubric_fix
bash refresh_official_data.sh
CAPSTONE_PYTHON="$(brew --prefix python@3.12)/bin/python3.12" bash setup_local.sh
bash collect_all_text.sh
```

The official IBM source dataset must have exactly **50 dealerships**, including Kansas. Verify `curl` output (never pretend 50 when the service has only 5).

- Q2: `evidence/text/django_server` must show **Starting development server at http://127.0.0.1:PORT/** and NOT a port conflict.
- Q6: JSON `{"userName":"","status":"Logged out"}`.
- Q8: Each review includes `purchase_date`.
- Q9: All 50 original IBM dealer records, copied without truncation. Text field can be large.
- Q14: `{"CarModels":[{"CarModel":"Camry","CarMake":"Toyota"},...]}` as per original assignment.
- Q1: The grader specifically asks for **`tdao7/fullstack_developer_capstone`**, not the old repo name. On your Mac run `gh repo rename fullstack_developer_capstone --repo tdao7/ibm-dealership-capstone --yes` if appropriate. Verify new URL before submission; **this changes the remote repository name and may require reconnecting Render**. Update local Git remote (`git remote set-url origin https://github.com/tdao7/fullstack_developer_capstone.git`), then push this corrected code.
- Q3/Q4: Both stylesheet links, About dealership description, Contact active nav, contact image.
- Q16–Q21 and Q24–Q27: screenshot must show requested actual content and where specified browser's true URL bar. Use macOS `--headed --mac-desktop` screenshot option. Avoid cropped forms/reviews.
- Q22: `.github/workflows/rubric-lint.yml` has two lint jobs; after pushing, verify GitHub Actions both jobs passed before submitting real workflow log.
- Q23: **Render is not accepted by this grader**. Use course lab URL or deploy to **IBM Cloud Code Engine** and submit actual `.codeengine.appdomain.cloud` domain.

## Capture screenshots with address bar on Mac

Start local Django in a separate terminal:

```bash
cd server && source .venv/bin/activate && python manage.py runserver 127.0.0.1:8000
```

In a second terminal:

```bash
source server/.venv/bin/activate
python -m pip install -r server/requirements-browser.txt
python -m playwright install chromium
python capture_screenshots.py --base-url http://127.0.0.1:8000 --headed --mac-desktop
```

Allow Terminal's **Screen Recording** permission. The script displays a real Chromium browser, screenshots the desktop containing the native URL/address bar, and reduces vertical whitespace to make tables, submit button, reviews and sentiment icons visible. Verify each PNG before re-submission.

**Do not capture Code Engine evidence until the real application works there.** The Render URL is useful for testing but is not sufficient for Q23 based on feedback.

## CI evidence (new two-job workflow)

After pushing the revised code to `tdao7/fullstack_developer_capstone` and confirming both jobs are green in GitHub Actions:

```bash
bash collect_ci.sh
pbcopy < evidence/text/CI_CD
```

Do not reuse the earlier `Django CI` one-job transcript; it was graded 1/3.

## Notes about local patching

If your existing project folder contains important `server/db.sqlite3`, `.venv`, `screenshots/` or previous evidence, do **not** delete the folder. Overlay the accompanying patch ZIP and keep those untracked files. Then run `refresh_official_data.sh`, activate the existing Python venv, and verify tests.

**IBM Cloud detailed guide:** [IBM_CODE_ENGINE_Q23_Q27.md](IBM_CODE_ENGINE_Q23_Q27.md). For remote captures, use `capture_cloud_screenshots.py --url "${DEPLOYMENT_URL}" --headed --mac-desktop` (registers a disposable course account if demo user isn't present).
