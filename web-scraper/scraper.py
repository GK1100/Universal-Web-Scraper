"""
scraper.py - Playwright-based headless browser scraping
Runs in an isolated thread to avoid event loop conflicts with Streamlit.
"""
import asyncio
import threading
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


async def _scrape_async(urls: list[str]) -> dict[str, str]:
    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        for url in urls:
            try:
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # Wait for body content to appear
                try:
                    await page.wait_for_selector("p, article, main", timeout=8000)
                except Exception:
                    pass
                await page.wait_for_timeout(3000)  # extra JS render time
                html = await page.content()
                results[url] = html
                print(f"  [OK] Scraped: {url}")
            except PlaywrightTimeout:
                print(f"  [TIMEOUT] Skipped: {url}")
                results[url] = ""
            except Exception as e:
                print(f"  [ERROR] {url} -> {e}")
                results[url] = ""
            finally:
                await page.close()
        await browser.close()
    return results


def scrape_pages(urls: list[str]) -> dict[str, str]:
    """
    Scrape each URL using Playwright in an isolated thread+event loop.
    Safe to call from Streamlit or any async context.
    """
    result_holder = {}

    def run():
        import sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result_holder.update(loop.run_until_complete(_scrape_async(urls)))
        finally:
            loop.close()

    t = threading.Thread(target=run)
    t.start()
    t.join()
    return result_holder
