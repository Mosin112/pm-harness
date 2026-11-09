#!/usr/bin/env python3
"""Build the PM Harness website.

Usage: build_site.py <owner/repo>

Reads site/index.src.html (a page fragment: head content, a `<!-- /head -->` marker, then body
content) and writes:
  docs/index.html                 full page for GitHub Pages
  docs/example/prototype.html     the worked example's clickable prototype
  docs/example/trees-view.html    the worked example's behaviour trees as a diagram
  docs/.nojekyll                  serve files as-is
  site/dist/index.html            the fragment with the repo filled in (for hosted previews)
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) != 2 or "/" not in sys.argv[1]:
        print(__doc__)
        return 2
    repo = sys.argv[1]
    src = (ROOT / "site" / "index.src.html").read_text(encoding="utf-8").replace("__REPO__", repo)
    head, sep, body = src.partition("<!-- /head -->")
    if not sep:
        print("site/index.src.html is missing the <!-- /head --> marker")
        return 1

    page = (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        f"{head.strip()}\n</head>\n<body>\n{body.strip()}\n</body>\n</html>\n"
    )
    docs = ROOT / "docs"
    (docs / "example").mkdir(parents=True, exist_ok=True)
    (docs / "index.html").write_text(page, encoding="utf-8")
    (docs / ".nojekyll").write_text("", encoding="utf-8")
    example = ROOT / "examples" / "price-alerts"
    shutil.copyfile(example / "04-prototype" / "index.html", docs / "example" / "prototype.html")
    shutil.copyfile(example / "03-trees-view.html", docs / "example" / "trees-view.html")

    dist = ROOT / "site" / "dist"
    (dist / "example").mkdir(parents=True, exist_ok=True)
    (dist / "index.html").write_text(src, encoding="utf-8")
    for name in ("prototype.html", "trees-view.html"):
        shutil.copyfile(docs / "example" / name, dist / "example" / name)
    print(f"Built docs/ and site/dist/ for {repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
