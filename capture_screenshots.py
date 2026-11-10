#!/usr/bin/env python3
"""Capture real pages from a RUNNING Django app, not fabricated screenshot graphics.

Install: pip install playwright && python -m playwright install chromium
Run: python capture_screenshots.py --base-url http://127.0.0.1:8000
     python capture_screenshots.py --base-url ... --deployment-url https://your-real-app.example
macOS full browser chrome: add --headed --mac-desktop (requires Screen Recording permission).
"""
import argparse, os, sys, subprocess, time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'screenshots'

parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default='http://127.0.0.1:8000')
parser.add_argument('--deployment-url',default=os.getenv('DEPLOYMENT_URL',''))
parser.add_argument('--username',default='capstone_demo')
parser.add_argument('--password',default=os.getenv('CAPSTONE_DEMO_PASSWORD','CapstoneDemo2026!'))
parser.add_argument('--admin-username',default='root')
parser.add_argument('--admin-password',default=os.getenv('CAPSTONE_ADMIN_PASSWORD','CourseAdmin2026!'))
parser.add_argument('--headed',action='store_true')
parser.add_argument('--mac-desktop',action='store_true',help='Take whole desktop image (including Chrome address bar) using screencapture; macOS only, requires --headed')
a=parser.parse_args()
if a.mac_desktop and not a.headed:parser.error('--mac-desktop also requires --headed')
OUT.mkdir(exist_ok=True)

def cap(page,filename):
 page.wait_for_timeout(450)
 path=OUT/filename
 if a.mac_desktop:
  subprocess.run(['screencapture','-x',str(path)],check=True)
 else:
  page.screenshot(path=str(path),full_page=False,animations='disabled')
 print(f'Saved: {path}')

def goto(page,base,path):
 page.goto(base.rstrip('/')+path,wait_until='domcontentloaded',timeout=20000)

def signin(page,base):
 goto(page,base,'/djangoapp/get_dealers')
 page.wait_for_function("document.querySelector('#countChip')?.textContent?.includes('dealerships found')",timeout=15000)
 page.locator('#loginBtn').click()
 page.locator('#loginUsername').fill(a.username)
 page.locator('#loginPassword').fill(a.password)
 page.locator('#loginForm button[type=submit]').click()
 page.locator('#navuser').get_by_text(a.username,exact=False).wait_for(timeout=15000)

def journey(context,base,deployed=False):
 page=context.new_page()
 goto(page,base,'/djangoapp/get_dealers')
 page.wait_for_function("document.querySelector('#countChip')?.textContent?.includes('dealerships found')",timeout=15000)
 cap(page,'deployed_landingpage.png' if deployed else 'get_dealers.png')
 signin(page,base)
 cap(page,'deployed_loggedin.png' if deployed else 'get_dealers_loggedin.png')
 page.locator('#stateFilter').select_option('Kansas')
 page.wait_for_function("document.querySelector('#countChip')?.textContent?.includes('dealerships found')",timeout=15000)
 cap(page,'dealersbystate.png') if not deployed else None
 page.locator('#dealerRows tr a.link').first.click()
 page.locator('#reviews .reviewcard').first.wait_for(timeout=15000)
 cap(page,'deployed_dealer_detail.png' if deployed else 'dealer_id_reviews.png')
 if not deployed:
  page.locator('#postBtn').click()
  page.locator('#review').fill('Fantastic services. Helpful team and transparent pricing. I recommend this dealership.')
  cap(page,'dealership_review_submission.png')
  page.locator('#submitReview').click()
  page.wait_for_url('**/djangoapp/reviews/dealer/*?posted=1',timeout=15000)
  page.get_by_text('Fantastic services. Helpful team and transparent pricing.',exact=False).first.wait_for(timeout=15000)
  cap(page,'added_review.png')
 else:
  page.locator('#postBtn').click()
  page.locator('#review').fill('Fantastic services. Excellent support and a smooth purchase.')
  page.locator('#submitReview').click()
  page.wait_for_url('**/djangoapp/reviews/dealer/*?posted=1',timeout=15000)
  page.get_by_text('Fantastic services. Excellent support',exact=False).first.wait_for(timeout=15000)
  cap(page,'deployed_add_review.png')
 page.close()

def admin(context,base):
 page=context.new_page()
 goto(page,base,'/admin/login/')
 page.locator('#id_username').fill(a.admin_username)
 page.locator('#id_password').fill(a.admin_password)
 page.locator('input[type=submit]').click()
 page.wait_for_url('**/admin/**',timeout=15000)
 if '/login' in page.url:raise RuntimeError('Admin login failed: confirm local root credentials')
 cap(page,'admin_login.png')
 # Django 5.x and earlier versions use a logout form or button
 form=page.locator('form[action$="/admin/logout/"]')
 if form.count()>0:
  form.locator('button,input[type=submit]').first.click()
 else:
  link=page.locator('a[href$="/admin/logout/"]')
  if link.count()>0:link.first.click()
  else:raise RuntimeError('No visible Logout control in Django Admin')
 page.get_by_text('Logged out',exact=False).first.wait_for(timeout=15000)
 cap(page,'admin_logout.png')
 page.close()

with sync_playwright() as p:
 browser=p.chromium.launch(headless=not a.headed,args=['--no-sandbox'] if sys.platform.startswith('linux') else [])
 try:
  ctx=browser.new_context(viewport={'width':1440,'height':900},device_scale_factor=1)
  admin(ctx,a.base_url)
  journey(ctx,a.base_url,False)
  if a.deployment_url:
   if not a.deployment_url.startswith('https://'):
    raise RuntimeError('--deployment-url must be a real public HTTPS URL')
   depctx=browser.new_context(viewport={'width':1440,'height':900},device_scale_factor=1)
   journey(depctx,a.deployment_url,True)
   depctx.close()
  else:
   print('Q24-Q27 skipped: no verified deployment URL supplied.')
  ctx.close()
 finally:browser.close()
