"""Fetch each public source, cache its text locally, and check every lesson quote.

Run:  .venv/bin/python scripts/verify_sources.py
The cache (cache/sources/) is gitignored: NODUS cites public post-mortems, it doesn't
redistribute them. Exit code 1 if any quote is not found verbatim.
"""
import html
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nodus.lessons import SOURCE_CACHE, load_lesson_file, load_sources, unverified_quotes  # noqa: E402


def page_text(url):
    # sec.gov asks automated clients to include a contact in the User-Agent (its fair-access
    # policy). Set NODUS_CONTACT="Your Name you@example.com" to fetch SEC pages.
    agent = "NODUS-source-check/1.0"
    if os.environ.get("NODUS_CONTACT"):
        agent += " " + os.environ["NODUS_CONTACT"]
    req = urllib.request.Request(url, headers={"User-Agent": agent})
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", errors="replace")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def main():
    sources = load_sources()
    SOURCE_CACHE.mkdir(parents=True, exist_ok=True)
    for doc_id, src in sources.items():
        if src["origin"] == "public" and not (SOURCE_CACHE / f"{doc_id}.txt").exists():
            print("fetching", src["url"])
            try:
                (SOURCE_CACHE / f"{doc_id}.txt").write_text(page_text(src["url"]))
            except urllib.error.HTTPError as e:
                hint = " (sec.gov: set NODUS_CONTACT, see the top of this file)" \
                    if "sec.gov" in src["url"] else ""
                print(f"   could not fetch ({e.code}){hint}")
    bad = 0
    for path in sorted(Path("data/lessons").glob("*.json")):
        lesson = load_lesson_file(path)
        problems = unverified_quotes(lesson, sources)
        quotes = sum(len(c.citations) for c in lesson.conditions)
        print(f"{lesson.id}: {quotes - len(problems)}/{quotes} quotes verified")
        for p in problems:
            print("   ", *p)
        bad += len(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
