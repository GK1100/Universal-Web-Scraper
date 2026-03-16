"""
extractor.py - Extract and structure content from raw HTML
"""
import re
import trafilatura
from bs4 import BeautifulSoup


def extract_metadata(html: str) -> dict:
    """Pull title, author, date from HTML meta tags."""
    soup = BeautifulSoup(html, "lxml")
    meta = {}

    # Title
    og_title = soup.find("meta", property="og:title")
    meta["title"] = (
        og_title["content"] if og_title
        else (soup.title.string.strip() if soup.title else "")
    )

    # Author
    author_tag = (
        soup.find("meta", attrs={"name": "author"}) or
        soup.find("meta", property="article:author")
    )
    meta["author"] = author_tag["content"] if author_tag else ""

    # Publish date
    date_tag = (
        soup.find("meta", property="article:published_time") or
        soup.find("meta", attrs={"name": "date"}) or
        soup.find("time")
    )
    if date_tag:
        meta["publish_date"] = date_tag.get("content") or date_tag.get("datetime") or date_tag.string or ""
    else:
        meta["publish_date"] = ""

    return meta


def extract_text(html: str) -> str:
    """Use trafilatura to extract main article text, with BS4 fallback."""
    # Try trafilatura first with favour_precision=False for better recall
    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
        favour_precision=False,
        include_formatting=False,
    )

    # Fallback: BeautifulSoup paragraph extraction
    if not text or len(text.strip()) < 100:
        soup = BeautifulSoup(html, "lxml")
        # Remove noise tags
        for tag in soup(["script", "style", "nav", "header", "footer",
                         "aside", "form", "noscript", "iframe"]):
            tag.decompose()
        # Grab all paragraphs
        paragraphs = [p.get_text(separator=" ").strip() for p in soup.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p) > 60]
        text = " ".join(paragraphs)

    if not text:
        return ""

    # Clean noise
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\t+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def summarize(text: str, max_sentences: int = 6) -> str:
    """Extractive summary: first N sentences, no trailing ellipsis."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 40]
    summary = ". ".join(sentences[:max_sentences])
    if summary and not summary.endswith("."):
        summary += "."
    return summary


def clean_snippet(snippet: str) -> str:
    """Remove trailing ellipsis and noise from search snippets."""
    snippet = re.sub(r"\s*\.{2,}\s*$", "", snippet.strip())
    snippet = re.sub(r"\s*…\s*$", "", snippet.strip())
    return snippet


def extract_key_points(text: str, max_points: int = 5) -> list[str]:
    """Extract key sentences heuristically."""
    # Split on sentence boundaries
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 60]
    key = []
    for s in sentences:
        if re.match(
            r"^(\d+[\.\)]|[-•*]|\b(How|Why|What|Key|Top|Best|Important|You should|Make sure|According|The|This|These)\b)",
            s, re.IGNORECASE
        ):
            key.append(s)
        if len(key) >= max_points:
            break
    # fallback: first N meaningful sentences
    if not key:
        key = sentences[:max_points]
    return key


def extract_topics(text: str) -> list[str]:
    """Naive topic extraction: most frequent meaningful words."""
    import re
    from collections import Counter
    STOPWORDS = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "is","are","was","were","be","been","being","have","has","had","do",
        "does","did","will","would","could","should","may","might","this",
        "that","these","those","it","its","we","you","they","he","she","i",
        "our","your","their","my","his","her","as","by","from","not","also",
        "can","more","about","which","when","how","what","all","one","if"
    }
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    freq = Counter(w for w in words if w not in STOPWORDS)
    return [w for w, _ in freq.most_common(8)]


def structure_content(url: str, html: str, search_meta: dict) -> dict:
    """Full pipeline: HTML -> structured dict."""
    snippet = clean_snippet(search_meta.get("snippet", ""))

    if not html:
        return {
            "website": url.split("/")[2] if "//" in url else url,
            "url": url,
            "title": search_meta.get("title", ""),
            "author": "",
            "publish_date": "",
            "content": "",
            "summary": snippet or "Could not load page.",
            "key_points": [],
            "topics": []
        }

    meta = extract_metadata(html)
    text = extract_text(html)
    summary = summarize(text) if text else snippet

    return {
        "website": url.split("/")[2] if "//" in url else url,
        "url": url,
        "title": meta["title"] or search_meta.get("title", ""),
        "author": meta["author"],
        "publish_date": meta["publish_date"],
        "content": text,
        "summary": summary,
        "key_points": extract_key_points(text),
        "topics": extract_topics(text)
    }
