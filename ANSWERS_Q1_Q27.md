# ANSWERS & SUBMISSION GUIDE — Q1–Q27

**Project:** IBM Full Stack Django/React Car Dealership Review Application  
**Repository owner:** `tdao7` (proposed repository, NOT YET published)

**READ FIRST:** Code for all 27 tasks is included; however, evidence cannot honestly be considered complete until Django is installed/run, the GitHub repository is published, CI passes, and a public cloud deployment exists. Browser screenshots must be captured from the actual app; the script does not fabricate images. Do not submit a proposed GitHub or deployment URL as if it already exists.

## Commands to run locally

```bash
bash setup_local.sh
# This creates demo users and checks Django tests.
bash collect_all_text.sh
python -m pip install -r server/requirements-browser.txt
python -m playwright install chromium
# Start Django in a separate terminal before screenshot collection:
cd server && source .venv/bin/activate && python manage.py runserver 127.0.0.1:8000
# From repository root in another terminal:
python capture_screenshots.py --base-url http://127.0.0.1:8000
```

*For Q17–Q19:* Playwright's built-in screenshot captures the webpage, not the native browser address bar. Capture manually in Chrome with the URL field visible, or use `--headed --mac-desktop` on macOS.

## Exact answer locations

| Question | Type | Answer file / URL | Additional requirement |
|---:|---|---|---|
| 1 | URL | `https://github.com/tdao7/ibm-dealership-capstone/blob/main/README.md` | Only after public GitHub publishing |
| 2 | TEXT | `evidence/text/django_server` | Real Django server log from collect_all_text.sh |
| 3 | URL | `https://github.com/tdao7/ibm-dealership-capstone/blob/main/server/frontend/static/About.html` | Only after public GitHub publishing |
| 4 | URL | `https://github.com/tdao7/ibm-dealership-capstone/blob/main/server/frontend/static/Contact.html` | Only after public GitHub publishing |
| 5 | TEXT | `evidence/text/loginuser` | Real curl + output showing Authenticated |
| 6 | TEXT | `evidence/text/logoutuser` | Real curl + output showing Logged out |
| 7 | URL | `https://github.com/tdao7/ibm-dealership-capstone/blob/main/server/frontend/src/components/Register/Register.jsx` | Only after public GitHub publishing |
| 8 | TEXT | `evidence/text/getdealerreviews` | Actual curl response with dealer reviews |
| 9 | TEXT | `evidence/text/getalldealers` | Actual curl response listing all dealers |
| 10 | TEXT | `evidence/text/getdealerbyid` | Actual curl response with dealer details |
| 11 | TEXT | `evidence/text/getdealersbyState` | Kansas dealer(s) from /djangoapp/get_dealers/Kansas |
| 12 | UPLOAD | `screenshots/admin_login.png` | Actual logged-in Django admin root page |
| 13 | UPLOAD | `screenshots/admin_logout.png` | Actual Django admin logout page |
| 14 | TEXT | `evidence/text/getallcarmakes` | All car makes/models returned by API |
| 15 | TEXT | `evidence/text/analyzereview` | Live sentiment result for Fantastic services |
| 16 | UPLOAD | `screenshots/get_dealers.png` | Home dealers visible before login |
| 17 | UPLOAD | `screenshots/get_dealers_loggedin.png` | Username + Review Dealer; address bar required |
| 18 | UPLOAD | `screenshots/dealersbystate.png` | State-filtered Kansas dealers; address bar required |
| 19 | UPLOAD | `screenshots/dealer_id_reviews.png` | Dealer details/reviews; address bar required |
| 20 | UPLOAD | `screenshots/dealership_review_submission.png` | Review form populated before submit |
| 21 | UPLOAD | `screenshots/added_review.png` | Review present after successful POST |
| 22 | TEXT | `evidence/text/CI_CD` | ONLY from an actual successful GitHub Actions run |
| 23 | TEXT | `evidence/text/deploymentURL` | ONLY after a real public deployment |
| 24 | UPLOAD | `screenshots/deployed_landingpage.png` | Actual live deployment home page |
| 25 | UPLOAD | `screenshots/deployed_loggedin.png` | Actual live logged-in page and username |
| 26 | UPLOAD | `screenshots/deployed_dealer_detail.png` | Actual live dealer details page |
| 27 | UPLOAD | `screenshots/deployed_add_review.png` | Actual live newly posted review |

## Ready-to-use GitHub URL templates

These strings are **not currently verified public links**:

```text
Q1 https://github.com/tdao7/ibm-dealership-capstone/blob/main/README.md
Q3 https://github.com/tdao7/ibm-dealership-capstone/blob/main/server/frontend/static/About.html
Q4 https://github.com/tdao7/ibm-dealership-capstone/blob/main/server/frontend/static/Contact.html
Q7 https://github.com/tdao7/ibm-dealership-capstone/blob/main/server/frontend/src/components/Register/Register.jsx
```

## Q11 / Q14 / Q15 cURL commands

```bash
# Q11
curl -sS http://127.0.0.1:8000/djangoapp/get_dealers/Kansas

# Q14 (task 14 and 15)
curl -sS http://127.0.0.1:8000/djangoapp/get_cars

# Q15 (task 16)
curl -sS http://127.0.0.1:5050/analyze/Fantastic%20services
```

The corresponding `.txt` output files are created by `bash collect_all_text.sh` using actual HTTP responses, not manually fabricated results.

## Q22: GitHub Actions

GitHub workflow source: `.github/workflows/django-ci.yml`. After publishing, navigate to GitHub → Actions and wait for a success. Then run `bash collect_ci.sh`, which saves a real job transcript as `evidence/text/CI_CD`. **Do not fabricate CI success output.**

## Q23–27: Public deployment

Build source: `Dockerfile`, `render.yaml`. Deploy using your own cloud service (Render, etc.) and configure a permanent database, allowed hosts, and a secret key. Only after the live HTTPS URL responds successfully:

```bash
export DEPLOYMENT_URL='https://your-actual-deployment.example'
bash collect_deployment_url.sh
python capture_screenshots.py --base-url http://127.0.0.1:8000 --deployment-url "$DEPLOYMENT_URL"
```

Q24–27 screenshots are not produced when deployment is absent.

## Grading limitations

- The seed dataset and sentiment analyzer are **educational substitutes** for the external MongoDB and Watson/Flask services from the original IBM instructions. They demonstrate the API shapes but should not be described as the original IBM cloud integration.
- Q17, Q18, Q19 require an address bar in the screenshot. An ordinary Playwright page-only screenshot does not satisfy that detail by itself.
- This archive does not contain invented GitHub URLs, successful Actions logs, cloud URLs or deployed screenshots.
- If your grading rubric requires the original cloud architecture, follow the course's external-service instructions and replace the local demonstration data/microservice before final submission.
