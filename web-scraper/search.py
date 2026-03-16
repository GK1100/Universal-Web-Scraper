"""
search.py - Web search + ad/spam filtering
"""
import re
from ddgs import DDGS

# Patterns to exclude from results
AD_PATTERNS = [
    r"ads\.", r"adservice", r"doubleclick", r"googleads",
    r"utm_", r"sponsored", r"tracking", r"click\.php",
    r"redirect\.", r"aff\.", r"affiliate"
]

EXCLUDED_DOMAINS = [
    "facebook.com", "twitter.com", "instagram.com", "tiktok.com",
    "linkedin.com", "reddit.com", "pinterest.com", "youtube.com",
    "login.", "signin.", "accounts."
]


def is_ad_or_spam(url: str) -> bool:
    for pattern in AD_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    for domain in EXCLUDED_DOMAINS:
        if domain in url:
            return True
    return False


def search_web(query: str, max_results: int = 10) -> list[dict]:
    """Search DuckDuckGo and return filtered results."""
    results = []
    ddgs = DDGS()
    raw = list(ddgs.text(query, max_results=max_results + 5))

    for i, r in enumerate(raw):
        url = r.get("href", "")
        if not url.startswith("http"):
            continue
        if is_ad_or_spam(url):
            continue
        results.append({
            "rank": i + 1,
            "title": r.get("title", ""),
            "url": url,
            "snippet": r.get("body", "")
        })
        if len(results) >= max_results:
            break

    return results
