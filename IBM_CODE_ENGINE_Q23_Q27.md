# Q23–Q27: Correct deployment target per grading feedback

Your prior Render URL was specifically rejected. The grader requests **the course lab URL OR an IBM Cloud Code Engine application URL**, not Render. Deploy the corrected GitHub repo to Code Engine, then produce new screenshots of that real deployment.

IBM documentation: https://cloud.ibm.com/docs/cli?topic=cli-cli and https://cloud.ibm.com/docs/codeengine?topic=codeengine-application-workloads

## 1. Preparation

1. Use your own IBM Cloud account with Code Engine permission and a selected resource group. Charges may apply. Alternatively use the course-provided lab URL if the lab provides a usable deployment endpoint.
2. Push the corrected code to the **public repository `tdao7/fullstack_developer_capstone`**, including the downloaded 50-dealership file.
3. Install the IBM Cloud CLI and Code Engine plugin from IBM documentation. Authenticate using `ibmcloud login` (or the SSO login method for your account). Select a suitable region with `ibmcloud target -r us-south`, adjusting for your account.

## 2. Code Engine CLI example

```bash
# Only run after successful IBM Cloud login and resource group targeting.
ibmcloud ce project create --name capstone-car-dealers
# Alternatively: ibmcloud ce project select --name YOUR_EXISTING_PROJECT

read -r -s -p 'Demo password (new, not the previous course password): ' CAPSTONE_CLOUD_PASSWORD
printf '\n'
export CAPSTONE_CLOUD_PASSWORD
DJANGO_KEY="$(python3 -c 'import secrets;print(secrets.token_urlsafe(55))')"

ibmcloud ce application create \
  --name bestcars-capstone \
  --build-source https://github.com/tdao7/fullstack_developer_capstone.git \
  --build-strategy dockerfile \
  --port 8000 \
  --visibility public \
  --env DJANGO_ALLOWED_HOSTS=.codeengine.appdomain.cloud \
  --env DJANGO_DEBUG=0 \
  --env DJANGO_SECRET_KEY="$DJANGO_KEY" \
  --env CAPSTONE_DEMO_PASSWORD="$CAPSTONE_CLOUD_PASSWORD"

ibmcloud ce application get --name bestcars-capstone --output url
unset DJANGO_KEY CAPSTONE_CLOUD_PASSWORD
```

The displayed HTTPS URL must have the real Code Engine shape:
`https://bestcars-capstone.<provider-unique-id>.<region>.codeengine.appdomain.cloud`.
Do not invent a URL or submit the placeholder literally. A valid public page is necessary, not just successful CLI output.

## 3. Verify and capture evidence

```bash
export DEPLOYMENT_URL='https://YOUR-ACTUAL-IBM-CODE-ENGINE-URL'
bash collect_deployment_url.sh
pbcopy < evidence/text/deploymentURL  # Q23

source server/.venv/bin/activate
python capture_cloud_screenshots.py --url "$DEPLOYMENT_URL" --headed --mac-desktop
open screenshots/
```

Screenshots should include **actual Chromium address bar** and site content:
- Q24 `deployed_landingpage.png`: dealer rows and Code Engine address visible.
- Q25 `deployed_loggedin.png`: dealer rows, username, and URL visible.
- Q26 `deployed_dealer_detail.png`: dealership details, reviews, and URL visible.
- Q27 `deployed_add_review.png`: posted review, sentiment icon, dealership details, and URL visible.

On Mac, grant Terminal permission under Settings → Privacy & Security → Screen & System Audio Recording. Check images before uploading.

**Caveat:** The demo uses SQLite on ephemeral container filesystem. Code Engine may restart/scale the container and lose new reviews. For a real service, configure persistent PostgreSQL; for the course capture screenshots immediately during the same active app session. Do not use real customer data.
