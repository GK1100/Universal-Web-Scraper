"""
main.py - Intelligent web scraping pipeline
Usage: python main.py "top 5 blogs about startup fundraising"
       python main.py "3 articles about electric vehicles"
       python main.py "best guides on personal finance"
"""
import sys
import re
import json
from search import search_web
from scraper import scrape_pages
from extractor import structure_content
from insights import aggregate_insights
from exporter import export


# ── 1. Parse natural language query ──────────────────────────────────────────

def parse_query(prompt: str) -> tuple[str, int]:
    """Extract search topic and desired result count from natural language."""
    prompt = prompt.strip()

    # Extract number if present (e.g. "top 5", "3 articles")
    match = re.search(r"\b(\d+)\b", prompt)
    count = int(match.group(1)) if match else 5

    # Strip common filler words to get clean search query
    clean = re.sub(
        r"\b(top|best|scrape|get|find|show|give me|list|articles?|blogs?|guides?|posts?|pages?|websites?|about|on|for|the)\b",
        "", prompt, flags=re.IGNORECASE
    )
    clean = re.sub(r"\d+", "", clean)          # remove numbers
    clean = re.sub(r"\s{2,}", " ", clean).strip()

    return clean, count


# ── 2. Display helpers ────────────────────────────────────────────────────────

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_result(i: int, r: dict):
    print(f"\n[{i}] {r['title']}")
    print(f"    URL     : {r['url']}")
    print(f"    Author  : {r['author'] or 'N/A'}")
    print(f"    Date    : {r['publish_date'] or 'N/A'}")
    print(f"    Summary : {r['summary']}")
    if r["key_points"]:
        print("    Key Points:")
        for kp in r["key_points"][:3]:
            print(f"      • {kp[:120]}")
    if r["topics"]:
        print(f"    Topics  : {', '.join(r['topics'])}")


# ── 3. Main pipeline ──────────────────────────────────────────────────────────

def run(prompt: str):
    # Step 1: Parse
    search_query, n = parse_query(prompt)
    print(f"\nPrompt   : {prompt}")
    print(f"Query    : {search_query}")
    print(f"Results  : {n}")

    # Step 2: Search
    print_section("Searching the web...")
    search_results = search_web(search_query, max_results=n + 5)
    print(f"Found {len(search_results)} results after filtering ads/spam.")

    if not search_results:
        print("No results found. Try a different query.")
        return

    # Step 3: Select top N
    selected = search_results[:n]

    print_section("Selected URLs")
    for r in selected:
        print(f"  {r['rank']}. {r['url']}")

    # Step 4: Scrape
    print_section("Scraping pages...")
    urls = [r["url"] for r in selected]
    html_map = scrape_pages(urls)

    # Step 5 & 6: Extract + Structure
    print_section("Extracting and structuring content...")
    structured = []
    search_meta_map = {r["url"]: r for r in selected}

    for url in urls:
        html = html_map.get(url, "")
        meta = search_meta_map.get(url, {})
        result = structure_content(url, html, meta)
        structured.append(result)
        print(f"  [DONE] {result['title'][:60]}")

    # Step 7: Insights
    print_section("Aggregated Insights")
    insights = aggregate_insights(structured)
    for line in insights:
        print(line)

    # Step 8: Present results
    print_section("Structured Results")
    for i, r in enumerate(structured, 1):
        print_result(i, r)

    # Step 9: Export
    json_path, csv_path = export(structured, search_query)
    print_section("Export Complete")
    print(f"  JSON : {json_path}")
    print(f"  CSV  : {csv_path}")

    # Also print raw JSON to stdout for piping
    print_section("Raw JSON Output")
    print(json.dumps(structured, indent=2, ensure_ascii=False))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<your query>\"")
        print("Examples:")
        print('  python main.py "top 5 blogs about startup fundraising"')
        print('  python main.py "3 articles about electric vehicles"')
        print('  python main.py "best guides on personal finance"')
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    run(user_prompt)
