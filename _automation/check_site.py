#!/usr/bin/env python3
"""Quality gate for TopMoneyApps automated publishing.

Usage:
    python3 _automation/check_site.py new-page.html [another.html ...]

Checks each named page against the publishing rules in .claude/CLAUDE.md, then runs
site-wide checks (valid JSON-LD everywhere, no broken internal links, valid sitemap).
Exits with status 1 and a list of problems if anything fails.
"""
import glob
import json
import os
import re
import sys
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

HUBS = ["investing-guides.html", "stats.html", "comparisons.html", "money-guides.html", "tools.html"]
FORBIDDEN = [r"lorem ipsum", r"\bTODO\b", r"\bTBD\b", r"\[citation", r"XX%", r"\{\{", r"as an ai",
             r"we tested", r"in our testing", r"hands-on test", r"our team tested"]
MIN_WORDS = 800


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def ld_blocks(html):
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        out.append(json.loads(m.group(1)))
    return out


def ld_types(blocks):
    types = []
    for b in blocks:
        for item in (b if isinstance(b, list) else b.get("@graph", [b])):
            t = item.get("@type")
            types += t if isinstance(t, list) else [t]
    return types


def visible_text(html):
    body = html[html.find("<body"):]
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))


def norm(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"').replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


def check_page(page, problems):
    p = lambda msg: problems.append(f"{page}: {msg}")
    if not os.path.exists(page):
        p("file not found")
        return
    html = read(page)
    slug = os.path.basename(page)
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.html", slug):
        p("file name must be a lowercase-hyphenated .html slug")
    if html.count("<h1") != 1:
        p(f"must have exactly one <h1> (found {html.count('<h1')})")
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    if not t or "| TopMoneyApps" not in t.group(1):
        p('<title> must end with "| TopMoneyApps"')
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not d or not (70 <= len(d.group(1)) <= 200):
        p("meta description missing or not 70-200 characters")
    canon = f"https://topmoneyapps.com/{slug}"
    if f'<link rel="canonical" href="{canon}"' not in html:
        p(f"canonical must be {canon}")
    if 'property="og:image"' not in html:
        p("missing og:image")
    if "G-W1RSS2P0EM" not in html:
        p("missing Google tag G-W1RSS2P0EM")
    if "<!-- geo:takeaways -->" not in html:
        p("missing <!-- geo:takeaways --> block")
    else:
        tk = html.split("<!-- geo:takeaways -->", 1)[1].split("<!-- /geo:takeaways -->", 1)[0]
        n = tk.count("<li")
        if not 3 <= n <= 6:
            p(f"Key Takeaways should have 3-5 bullets (found {n})")
    if "<!-- geo:sources -->" not in html:
        p("missing <!-- geo:sources --> block")
    else:
        src = html.split("<!-- geo:sources -->", 1)[1].split("<!-- /geo:sources -->", 1)[0]
        ext = set(re.findall(r'href="(https?://(?!topmoneyapps\.com)[^"]+)"', src))
        if len(ext) < 3:
            p(f"Sources must link at least 3 external sources (found {len(ext)})")
    text = visible_text(html)
    words = len(text.split())
    if words < MIN_WORDS:
        p(f"only {words} words of visible text (minimum {MIN_WORDS})")
    if "Mike Van Kempen" not in text:
        p("missing Mike Van Kempen byline")
    for pat in FORBIDDEN:
        if re.search(pat, text, re.I):
            p(f"contains forbidden text matching '{pat}'")
    if "acorns" in slug or (t and re.search(r"\bacorns\b", t.group(1), re.I)):
        p("Acorns-focused pages are not published automatically (log as 'needs Mike')")
    try:
        blocks = ld_blocks(html)
    except json.JSONDecodeError as e:
        p(f"invalid JSON-LD: {e}")
        blocks = []
    types = ld_types(blocks)
    for needed in ["Article", "BreadcrumbList", "FAQPage"]:
        if needed not in types:
            p(f"missing JSON-LD {needed}")
    for b in blocks:
        items = b if isinstance(b, list) else b.get("@graph", [b])
        for it in items:
            if it.get("@type") == "Article":
                a = it.get("author") or {}
                if (a.get("name") if isinstance(a, dict) else None) != "Mike Van Kempen":
                    p("Article author must be Mike Van Kempen")
                if not it.get("datePublished") or not it.get("dateModified"):
                    p("Article needs datePublished and dateModified")
            if it.get("@type") == "FAQPage":
                qs = it.get("mainEntity", [])
                if not 3 <= len(qs) <= 8:
                    p(f"FAQPage should have 3-6 questions (found {len(qs)})")
                vis = norm(text)
                for q in qs:
                    if norm(q.get("name", "")) not in vis:
                        p(f"FAQ question not visible on page: {q.get('name', '')[:60]}")
    internal = {h for h in re.findall(r'href="/?([a-z0-9-]+\.html)(?:#[^"]*)?"', html) if h != slug}
    if len(internal) < 3:
        p(f"needs at least 3 internal links to other pages (found {len(internal)})")
    if 'rel="sponsored' in html and not re.search(r"affiliate|commission", text, re.I):
        p("has sponsored links but no affiliate disclosure")
    # wiring
    if f"<loc>{canon}</loc>" not in read("sitemap.xml"):
        p("not listed in sitemap.xml")
    if canon not in read("llms.txt"):
        p("not listed in llms.txt")
    if f"URL: {canon}" not in read("llms-full.txt"):
        p("no block in llms-full.txt")
    if not any(f'href="{slug}"' in read(h) or f'href="/{slug}"' in read(h) for h in HUBS if os.path.exists(h)):
        p("not linked from any hub page (" + ", ".join(HUBS) + ")")
    others = [f for f in glob.glob("*.html") if f != slug and f not in HUBS and f != "index.html"]
    if not any(f'href="{slug}"' in read(f) for f in others):
        p("no related existing page links to it yet")


def check_site(problems):
    for f in sorted(glob.glob("*.html")):
        html = read(f)
        try:
            ld_blocks(html)
        except json.JSONDecodeError as e:
            problems.append(f"{f}: invalid JSON-LD ({e})")
        for h in set(re.findall(r'href="/?([a-zA-Z0-9_-]+\.html)(?:#[^"]*)?"', html)):
            if not os.path.exists(h):
                problems.append(f"{f}: broken internal link -> {h}")
    try:
        sm = read("sitemap.xml")
        xml.dom.minidom.parseString(sm)
        for loc in re.findall(r"<loc>https://topmoneyapps\.com/([^<]*)</loc>", sm):
            if loc and not os.path.exists(loc):
                problems.append(f"sitemap.xml lists a missing page: {loc}")
    except Exception as e:  # noqa: BLE001
        problems.append(f"sitemap.xml is not valid XML: {e}")


def main():
    problems = []
    for page in sys.argv[1:]:
        check_page(page, problems)
    check_site(problems)
    if problems:
        print(f"{len(problems)} PROBLEM(S):")
        for x in problems:
            print(" -", x)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
