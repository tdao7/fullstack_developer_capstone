#!/usr/bin/env python3
"""Capture Q24-Q27 as REAL screenshots from the user's live Render deployment.

Usage (from project root):
    server/.venv/bin/python ~/Downloads/capture_render_4.py \
       --url https://ibm-dealership-capstone.onrender.com

Requires: pip install playwright; python -m playwright install chromium.

If the demo credentials are not configured on Render, this script registers a
random test user through the deployed app's real registration API, logs in via
its UI, and posts a real review. It does not create synthetic screenshots.
"""
import argparse
import secrets
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

p = argparse.ArgumentParser(description='Capture 4 live deployment screenshots')
p.add_argument('--url', default='https://ibm-dealership-capstone.onrender.com')
p.add_argument('--output', default='screenshots')
p.add_argument('--username', default='capstone_demo')
p.add_argument('--password', default='CapstoneDemo2026!')
p.add_argument('--headed', action='store_true', help='Show the Chromium browser while capturing')
p.add_argument('--mac-desktop', action='store_true', help='Capture actual macOS desktop with Chromium address bar; requires --headed')
a = p.parse_args()
if a.mac_desktop and not a.headed: p.error('--mac-desktop requires --headed')
base = a.url.rstrip('/')
if not base.startswith('https://'):
    p.error('Expected real HTTPS deployment URL')
out = Path(a.output).expanduser().resolve()
out.mkdir(parents=True, exist_ok=True)


def visit(page, route, checks=None):
    url = base + route
    last_error = None
    for attempt in range(3):
        try:
            resp = page.goto(url, wait_until='domcontentloaded', timeout=65000)
            if resp is None or resp.status >= 400:
                raise RuntimeError(f'HTTP {resp.status if resp else "no response"} from {url}')
            if checks:
                page.locator(checks).first.wait_for(state='visible', timeout=25000)
            return
        except Exception as ex:
            last_error = ex
            if attempt < 2:
                print(f'  Waiting for Render to start (attempt {attempt + 1}): {str(ex)[:120]}', flush=True)
                page.wait_for_timeout(3500)
    raise RuntimeError(f'Cannot load {url}: {last_error}')


def compact(page):
    # Genuine server-rendered data with a denser viewport; never draws fake URL chrome.
    page.add_style_tag(content='''
        .hero{padding:14px 24px!important} .hero h1{font-size:28px!important;margin:4px 0!important}
        .hero p{font-size:13px!important}.statrow{margin:7px 0!important}
        .navin{height:58px!important}.main{margin:14px auto 24px!important}
        .panel{padding:13px!important}.toolbar{margin-bottom:8px!important}
        .table th,.table td{padding:7px 9px!important}.endpoint{margin:5px 0!important}
        .reviewcard{padding:9px 0!important}
    ''')
    page.evaluate("document.documentElement.style.zoom='0.76'")
    page.evaluate('window.scrollTo(0,0)')


def saved(page, name, focus=None):
    if focus:
        focus.scroll_into_view_if_needed(timeout=15000)
        page.wait_for_timeout(350)
    compact(page)
    path = out / name
    if a.mac_desktop:
        page.bring_to_front()
        page.wait_for_timeout(700)
        subprocess.run(['screencapture','-x','-D','1',str(path)],check=True)
    else:
        page.screenshot(path=str(path), full_page=name == 'deployed_add_review.png', animations='disabled')
    print(f'SAVED: {path}', flush=True)


def login_ui(page, username, password):
    visit(page, '/djangoapp/get_dealers', '#countChip')
    page.wait_for_function("document.querySelector('#countChip')?.textContent?.includes('dealerships found')", timeout=25000)
    if page.locator('#loginBtn').count() == 0:
        # If the browser is already logged in in this context, don't claim credentials were checked.
        if username in page.locator('#navuser').inner_text():
            return True
        return False
    page.locator('#loginBtn').click()
    page.locator('#loginUsername').fill(username)
    page.locator('#loginPassword').fill(password)
    page.locator('#loginForm button[type="submit"]').click()
    try:
        page.locator('#navuser .userpill').get_by_text(username, exact=False).wait_for(timeout=10000)
        return True
    except PWTimeout:
        return False


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=not a.headed)
    context = browser.new_context(viewport={'width': 1440, 'height': 980}, device_scale_factor=1)
    page = context.new_page()
    try:
        print('Checking real Render website:', base, flush=True)
        visit(page, '/djangoapp/get_dealers', '#countChip')
        page.wait_for_function("document.querySelector('#countChip')?.textContent?.includes('dealerships found')", timeout=25000)
        visit(page, '/', '#countChip')
        page.wait_for_function("document.querySelector('#countChip')?.textContent?.includes('dealerships found')", timeout=25000)
        page.locator('#dealerRows tr td').first.wait_for(timeout=20000)
        saved(page, 'deployed_landingpage.png')

        username, password = a.username, a.password
        print('Logging in through deployed website...', flush=True)
        if not login_ui(page, username, password):
            username = 'capstone_' + secrets.token_hex(4)
            password = secrets.token_urlsafe(18)
            print('Default demo login unavailable. Registering a new training account:', username, flush=True)
            reg = context.request.post(base + '/djangoapp/register',
                data={'userName':username,'firstName':'Course','lastName':'Learner',
                      'email':username + '@example.invalid','password':password},
                headers={'Content-Type':'application/json'}, timeout=40000)
            if reg.status != 201:
                raise RuntimeError(f'Cloud registration failed HTTP {reg.status}: {reg.text()[:450]}. '
                                   'Check Render logs and database permissions.')
            if not login_ui(page, username, password):
                raise RuntimeError('Registered successfully but cannot log in through cloud UI.')
        page.locator('#navuser .userpill').get_by_text(username, exact=False).wait_for(timeout=15000)
        page.locator('#dealerRows tr td').first.wait_for(timeout=20000)
        saved(page, 'deployed_loggedin.png')

        print('Loading dealer details and posted reviews...', flush=True)
        visit(page, '/djangoapp/reviews/dealer/1', '#reviews .reviewcard')
        page.wait_for_function("(document.querySelector('#detailHeading')?.textContent || '').trim().length > 3 && !document.querySelector('#detailHeading').textContent.includes('Loading')", timeout=20000)
        saved(page, 'deployed_dealer_detail.png')

        print('Submitting a real course review...', flush=True)
        visit(page, '/postreview/1', '#review')
        unique_marker = secrets.token_hex(3)
        review_text = f'Fantastic services. Helpful team and clear pricing. Capstone cloud review {unique_marker}.'
        page.locator('#review').fill(review_text)
        page.locator('#submitReview').click()
        page.wait_for_url('**/djangoapp/reviews/dealer/1?posted=1', timeout=25000)
        found = page.locator('.reviewcard', has_text=unique_marker)
        found.wait_for(state='visible', timeout=25000)
        saved(page, 'deployed_add_review.png', focus=found)

        print('\nDONE: all four files came from the live deployed website.', flush=True)
        print('Folder:', out, flush=True)
    except Exception as error:
        print('\nFAILED:', error, file=sys.stderr)
        print('Screenshots already saved may still be useful, but do NOT submit an error page as evidence.', file=sys.stderr)
        sys.exit(1)
    finally:
        context.close()
        browser.close()
