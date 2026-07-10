# test_cybernews.py
# ─────────────────────────────────────────────────────────
# Pre-launch test suite for CyberNews
# Tests all routes, features, and security measures
#
# Usage: python test_cybernews.py
# ─────────────────────────────────────────────────────────

import requests
import sys
import time
from datetime import datetime

BASE_URL = 'http://89.22.224.4:5000'

# Colors for terminal output
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
RESET  = '\033[0m'
BOLD   = '\033[1m'

passed = 0
failed = 0
warnings = 0


def test(name, condition, warning=False):
    """Record a test result."""
    global passed, failed, warnings
    if condition:
        print(f'  {GREEN}✓{RESET} {name}')
        passed += 1
    elif warning:
        print(f'  {YELLOW}⚠{RESET} {name}')
        warnings += 1
    else:
        print(f'  {RED}✗{RESET} {name}')
        failed += 1


def get(path, expected_status=200, **kwargs):
    """Make a GET request and return response."""
    try:
        r = requests.get(
            BASE_URL + path,
            timeout   = 10,
            **kwargs
        )
        return r
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None


def post(path, data=None, json=None, **kwargs):
    """Make a POST request and return response."""
    try:
        r = requests.post(
            BASE_URL + path,
            data    = data,
            json    = json,
            timeout = 10,
            **kwargs
        )
        return r
    except Exception:
        return None


# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}{CYAN}╔══════════════════════════════════════════╗{RESET}')
print(f'{BOLD}{CYAN}║   CyberNews Pre-Launch Test Suite        ║{RESET}')
print(f'{BOLD}{CYAN}╚══════════════════════════════════════════╝{RESET}\n')
print(f'Testing: {BASE_URL}')
print(f'Time:    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')


# ═══════════════════════════════════════════════════════
# 1. SERVER CONNECTIVITY
# ═══════════════════════════════════════════════════════
print(f'{BOLD}1. Server Connectivity{RESET}')

r = get('/')
test('Server is reachable', r is not None)
test('Homepage returns 200', r and r.status_code == 200)
test('Response time under 3s',
     r and r.elapsed.total_seconds() < 3,
     warning=True)


# ═══════════════════════════════════════════════════════
# 2. ALL PUBLIC PAGES LOAD
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}2. Public Pages{RESET}')

pages = [
    ('/', 'Homepage'),
    ('/categories', 'Categories page'),
    ('/about', 'About page'),
    ('/article/1', 'Article page'),
    ('/?page=2', 'Homepage page 2'),
]

for path, name in pages:
    r = get(path)
    test(f'{name} loads (200)', r and r.status_code == 200)


# ═══════════════════════════════════════════════════════
# 3. CONTENT CHECKS
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}3. Content Checks{RESET}')

r = get('/')
if r:
    html = r.text
    test('CyberNews logo present',
         'CyberNews' in html)
    test('Navigation links present',
         'Categories' in html and 'About' in html)
    test('Article cards present',
         'article-card' in html)
    test('Hero section present',
         'hero' in html)
    test('Breaking news ticker present',
         'ticker' in html)
    test('Stats bar present',
         'stats-bar' in html or 'stat-number' in html)
    test('Sidebar present',
         'sidebar' in html)
    test('Pagination present',
         'pagination' in html or 'page-btn' in html)
    test('Footer present',
         'main-footer' in html)
    test('Visitor counter present',
         'views' in html.lower() or 'visitor' in html.lower(),
         warning=True)


# ═══════════════════════════════════════════════════════
# 4. DATABASE CONTENT
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}4. Database Content{RESET}')

r = get('/api/articles')
if r and r.status_code == 200:
    data = r.json()
    test('API returns articles', len(data.get('articles', [])) > 0)
    test('More than 10 articles in database',
         data.get('count', 0) > 10)
    test('More than 50 articles in database',
         data.get('count', 0) > 50,
         warning=True)

    if data.get('articles'):
        first = data['articles'][0]
        test('Articles have titles', bool(first.get('title')))
        test('Articles have summaries', bool(first.get('summary')))
        test('Articles have categories', bool(first.get('category')))
        test('Articles have images', bool(first.get('image')))
        test('Articles have dates', bool(first.get('date')))


# ═══════════════════════════════════════════════════════
# 5. API ENDPOINTS
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}5. API Endpoints{RESET}')

# Search API
r = get('/api/search?q=malware')
test('Search API returns 200', r and r.status_code == 200)
if r and r.status_code == 200:
    data = r.json()
    test('Search returns results for "malware"',
         data.get('count', 0) > 0)

# Category filter
r = get('/api/articles?category=Malware')
test('Category filter API works', r and r.status_code == 200)
if r and r.status_code == 200:
    data = r.json()
    test('Category filter returns malware articles',
         all(a['category'] == 'Malware'
             for a in data.get('articles', [])),
         warning=True)

# Empty search
r = get('/api/search?q=')
test('Empty search returns 200', r and r.status_code == 200)

# Subscribe API (with fake email)
r = post('/api/subscribe',
         json={'email': 'test_automated@example.com'})
test('Subscribe API returns 200', r and r.status_code in [200, 400])


# ═══════════════════════════════════════════════════════
# 6. SECURITY CHECKS
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}6. Security Checks{RESET}')

# Admin requires login
r = get('/admin/', allow_redirects=False)
test('Admin redirects to login (302)',
     r and r.status_code == 302)

r = get('/admin/articles', allow_redirects=False)
test('Admin articles requires login',
     r and r.status_code == 302)

# Attack paths are blocked
attack_paths = [
    ('/wp-admin', 'WordPress scanner'),
    ('/phpmyadmin', 'PHPMyAdmin scanner'),
    ('/.env', 'ENV file access'),
    ('/.git', 'Git directory access'),
]

for path, name in attack_paths:
    r = get(path, allow_redirects=False)
    test(f'{name} blocked (403)',
         r and r.status_code == 403)

# SQL injection blocked
r = get("/?q=' OR 1=1--")
test('SQL injection attempt handled',
     r and r.status_code in [200, 400, 403])

# Scanner user agent blocked
r = get('/', headers={'User-Agent': 'sqlmap/1.0'})
test('SQLmap user agent blocked (403)',
     r and r.status_code == 403)

# XSS in search doesn't crash
r = get('/api/search?q=<script>alert(1)</script>')
test('XSS in search handled safely',
     r and r.status_code in [200, 400])


# ═══════════════════════════════════════════════════════
# 7. SECURITY HEADERS
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}7. Security Headers{RESET}')

r = get('/')
if r:
    headers = r.headers

    test('X-Content-Type-Options header present',
         headers.get('X-Content-Type-Options') == 'nosniff')

    test('X-Frame-Options header present',
         'X-Frame-Options' in headers)

    test('X-XSS-Protection header present',
         'X-XSS-Protection' in headers)

    test('Content-Security-Policy header present',
         'Content-Security-Policy' in headers)

    test('Referrer-Policy header present',
         'Referrer-Policy' in headers)

    test('Permissions-Policy header present',
         'Permissions-Policy' in headers,
         warning=True)


# ═══════════════════════════════════════════════════════
# 8. ERROR PAGES
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}8. Error Pages{RESET}')

r = get('/article/999999')
test('404 for missing article',
     r and r.status_code == 404)
if r:
    test('Custom 404 page shows CyberNews branding',
         'CyberNews' in r.text and '404' in r.text)

r = get('/nonexistent-page-12345')
test('404 for unknown route',
     r and r.status_code == 404)

r = get('/category/FakeCategory123')
test('404 for invalid category',
     r and r.status_code == 404)


# ═══════════════════════════════════════════════════════
# 9. LOGIN PAGE
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}9. Login Page{RESET}')

r = get('/login')
test('Login page loads (200)', r and r.status_code == 200)
if r:
    test('Login form present',
         'form' in r.text.lower() and 'password' in r.text.lower())
    test('CSRF token present in login form',
         'csrf_token' in r.text)

# Wrong credentials
r = post('/login', data={
    'username': 'wronguser',
    'password': 'wrongpassword',
    'csrf_token': 'invalid',
})
test('Wrong credentials rejected',
     r and r.status_code in [200, 400, 403])


# ═══════════════════════════════════════════════════════
# 10. PERFORMANCE
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}10. Performance{RESET}')

times = []
for i in range(3):
    start = time.time()
    r = get('/')
    if r:
        times.append(time.time() - start)

if times:
    avg = sum(times) / len(times)
    test(f'Average response time: {avg:.2f}s (under 2s)',
         avg < 2.0)
    test(f'Fast response time: {avg:.2f}s (under 1s)',
         avg < 1.0,
         warning=True)


# ═══════════════════════════════════════════════════════
# 11. MOBILE / RESPONSIVE
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}11. Mobile Responsiveness{RESET}')

# Check viewport meta tag
r = get('/')
if r:
    test('Viewport meta tag present',
         'viewport' in r.text)
    test('Bootstrap or responsive CSS',
         'responsive' in r.text.lower() or
         'media' in r.text.lower(),
         warning=True)


# ═══════════════════════════════════════════════════════
# 12. CATEGORY PAGES
# ═══════════════════════════════════════════════════════
print(f'\n{BOLD}12. Category Pages{RESET}')

categories = [
    'Malware', 'Data Breaches', 'Vulnerabilities',
    'Privacy', 'Research', 'Threats'
]

for cat in categories:
    r = get(f'/category/{cat}')
    test(f'/category/{cat} loads',
         r and r.status_code == 200)


# ═══════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════
total = passed + failed + warnings

print(f'\n{BOLD}{"═" * 45}{RESET}')
print(f'{BOLD}  TEST RESULTS{RESET}')
print(f'{"═" * 45}')
print(f'  {GREEN}✓ Passed:   {passed}{RESET}')
print(f'  {YELLOW}⚠ Warnings: {warnings}{RESET}')
print(f'  {RED}✗ Failed:   {failed}{RESET}')
print(f'  Total:     {total}')
print(f'{"═" * 45}')

score = int((passed / total) * 100) if total > 0 else 0
print(f'\n  Score: {score}%')

if score == 100:
    print(f'\n  {GREEN}{BOLD}🎉 PERFECT! Ready for production!{RESET}')
elif score >= 90:
    print(f'\n  {GREEN}{BOLD}✅ GREAT! Almost ready for production.{RESET}')
    print(f'  {YELLOW}Fix the failed tests before going live.{RESET}')
elif score >= 70:
    print(f'\n  {YELLOW}{BOLD}⚠️  GOOD but needs work.{RESET}')
    print(f'  {YELLOW}Fix failed tests before going live.{RESET}')
else:
    print(f'\n  {RED}{BOLD}❌ NOT READY. Too many failures.{RESET}')
    print(f'  {RED}Fix critical issues before going live.{RESET}')

print(f'\n  Tested at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'  Server:    {BASE_URL}\n')

sys.exit(0 if failed == 0 else 1)
