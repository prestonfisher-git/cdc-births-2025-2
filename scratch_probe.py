import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    page.goto('http://localhost:8501', wait_until='networkidle')
    page.wait_for_timeout(2000)

    ms = page.locator('[data-testid="stMultiSelect"]').first
    # Print all aria-labels of buttons and icons inside ms
    for el in ms.locator('button, [role="button"], svg').all():
        tag = el.evaluate('e => e.tagName')
        aria = el.evaluate('e => e.getAttribute("aria-label")')
        title = el.evaluate('e => e.getAttribute("title")')
        testid = el.evaluate('e => e.getAttribute("data-testid")')
        cls = el.evaluate('e => e.className')
        if "clear" in str(aria).lower() or "clear" in str(title).lower() or testid or tag == "BUTTON":
            print(f"Tag={tag}, aria={aria}, title={title}, testid={testid}")

    browser.close()
