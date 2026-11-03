
import csv
import hashlib
import os
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from playwright.sync_api import sync_playwright

RAW = Path("data/raw/handbook")
MANIFEST = Path("data/manifest.csv")

DELAY = 2
robots = {}


def allowed(url):
    root = "{0.scheme}://{0.netloc}".format(urlparse(url))

    if root not in robots:
        rp = RobotFileParser(root + "/robots.txt")

        try:
            rp.read()
        except Exception:
            rp = None

        robots[root] = rp

    rp = robots[root]
    return rp is None or rp.can_fetch(
        "ExamateStudentProject/1.0", url
    )


def name_for(url):
    parsed = urlparse(url)

    # Include the website name to avoid filename collisions.
    site = parsed.netloc.replace(".", "_")
    path = parsed.path.strip("/").replace("/", "__")

    if not path:
        path = "homepage"

    return f"{site}__{path}.pdf"


def main(list_file):
    RAW.mkdir(parents=True, exist_ok=True)

    new_manifest = not MANIFEST.exists()

    with open(MANIFEST, "a", newline="", encoding="utf-8") as mf:
        log = csv.writer(mf)

        if new_manifest:
            log.writerow([
                "file",
                "source_url",
                "downloaded_on",
                "bytes",
                "sha256"
            ])

        with open(list_file, encoding="utf-8") as fh:
            urls = [
                line.strip()
                for line in fh
                if line.strip() and not line.strip().startswith("#")
            ]

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()

            for index, url in enumerate(urls, start=1):
                if not allowed(url):
                    print("Blocked by robots.txt:", url)
                    continue

                output_file = RAW / name_for(url)

                if output_file.exists():
                    print("Already exists:", output_file)
                    continue

                try:
                    print(f"[{index}/{len(urls)}] Converting:", url)

                    response = page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=60000
                    )

                    if response is None or not response.ok:
                        print("Failed to load:", url)
                        continue

                    # Wait for page fonts to load.
                    page.evaluate(
                        "() => document.fonts.ready.then(() => true)"
                    )

                    # Save the rendered webpage as PDF.
                    page.pdf(
                        path=str(output_file),
                        format="A4",
                        print_background=True,
                        prefer_css_page_size=True
                    )

                    content = output_file.read_bytes()
                    digest = hashlib.sha256(content).hexdigest()[:16]

                    log.writerow([
                        str(output_file),
                        url,
                        date.today().isoformat(),
                        len(content),
                        digest
                    ])
                    mf.flush()

                    print("Saved PDF:", output_file)

                except Exception as error:
                    print("Failed:", url, error)

                time.sleep(DELAY)

            browser.close()

    print("\nPDF conversion completed.")
    print("PDF folder:", RAW)
    print("Manifest:", MANIFEST)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/download.py urls.txt")
        sys.exit(1)

    main(sys.argv[1])
