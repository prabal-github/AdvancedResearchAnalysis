#!/usr/bin/env python3
import requests

BASE_URL = "http://127.0.0.1:5008"

session = requests.Session()

print("Logging in as investor@demo.com ...")
resp = session.post(f"{BASE_URL}/investor_login", data={
    'email': 'investor@demo.com',
    'password': 'investor123'
}, allow_redirects=False)
print("Login status:", resp.status_code, resp.headers.get('Location'))

pages = [
    "/scenario_analysis_dashboard",
    "/run_backtest",
    "/backtest_dashboard",
]

for path in pages:
    url = f"{BASE_URL}{path}"
    r = session.get(url, allow_redirects=False)
    loc = r.headers.get('Location')
    print(f"GET {path}: {r.status_code} {'-> ' + loc if loc else ''}")
    if r.status_code == 200:
        # brief content hint
        print(f"   Content length: {len(r.text)}")
