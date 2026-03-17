# AI Web Scraper

An intelligent web scraping pipeline that takes a natural language query and returns fully structured data from multiple web sources — with filtering, extraction, summarization, and export.

---

## Features

- Natural language query parsing ("top 5 blogs about startup fundraising")
- DuckDuckGo search with automatic ad/spam/social media filtering
- Headless browser scraping via Playwright (handles JS-rendered pages)
- Content extraction using Trafilatura + BeautifulSoup fallback
- Structured output per article: title, author, date, content, summary, key points, topics
- Cross-source insight aggregation
- Streamlit UI + CLI support
- Export to JSON and CSV

---

## Project Structure

```
web-scraper/
├── app.py            # Streamlit UI
├── main.py           # CLI entry point
├── search.py         # DuckDuckGo search + filtering
├── scraper.py        # Playwright headless browser scraper
├── extractor.py      # Content extraction and structuring
├── insights.py       # Cross-source theme aggregation
├── exporter.py       # JSON / CSV export
├── requirements.txt
└── output/           # Saved results (auto-created)
```

---

## Setup

**1. Create and activate the conda environment**

```bash
conda create -n ai_scraping python=3.11 -y
conda activate ai_scraping
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Install Playwright browser**

```bash
playwright install chromium
```

---

## Usage

### Streamlit UI

```bash
conda activate ai_scraping
cd web-scraper
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### CLI

```bash
conda activate ai_scraping
cd web-scraper
python main.py "top 5 blogs about startup fundraising"
python main.py "3 articles about electric vehicles"
python main.py "best guides on personal finance"
```

---

## Output Schema

Each scraped result follows this structure:

```json
{
  "website": "example.com",
  "url": "https://...",
  "title": "Article title",
  "author": "Author name",
  "publish_date": "2024-01-01",
  "content": "Full extracted article text...",
  "summary": "First few sentences summarizing the article...",
  "key_points": ["Point one", "Point two"],
  "topics": ["keyword1", "keyword2"]
}
```

Results are saved to `output/` as both `.json` and `.csv` after every run.

---

## Requirements

| Package | Purpose |
|---|---|
| `ddgs` | DuckDuckGo search API |
| `playwright` | Headless browser scraping |
| `trafilatura` | Main content extraction |
| `beautifulsoup4` | HTML parsing / fallback extraction |
| `lxml` | HTML parser |
| `streamlit` | Web UI |
| `requests` | HTTP requests |
| `nltk` | NLP utilities |
| `sumy` | Text summarization |

---

## Deploy on Render

**1. Push to GitHub**

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

**2. Create a new Web Service on [Render](https://render.com)**

- Connect your GitHub repo
- Set **Environment** to `Docker`
- Set **Dockerfile path** to `web-scraper/Dockerfile`
- Set **Port** to `8501`

**3. Deploy**

Render will build the Docker image and deploy automatically. Your app will be live at `https://your-app.onrender.com`.

> Note: Render's free tier spins down after inactivity. Use a paid plan for always-on scraping.

### Local Docker test

```bash
cd web-scraper
docker build -t ai-scraper .
docker run -p 8501:8501 ai-scraper
```

Open `http://localhost:8501`.
