from pathlib import Path

import os
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright

import re

ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as p, TemporaryDirectory() as temp:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH"))
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto((ROOT / "index.html").as_uri())
    page.locator("#size").select_option("US Letter")
    page.locator("#pattern").select_option("Dots")
    assert page.locator("pattern circle").count() == 1
    assert page.locator("pattern").get_attribute("width") == "5"
    pdf = page.pdf(prefer_css_page_size=True)
    dims = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([.\d]+)\s+([.\d]+)", pdf)
    assert dims and all(
        abs(float(n) - v) < 2 for n, v in zip(dims.groups(), [612, 792])
    )
    assert len(re.findall(rb"/Type\s*/Page\b", pdf)) == 1
    assert not errors, errors
    browser.close()
