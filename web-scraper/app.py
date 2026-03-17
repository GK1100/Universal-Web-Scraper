"""
app.py - Streamlit UI for the intelligent web scraping pipeline
"""
import sys
import os
import json
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from main import parse_query
from search import search_web
from scraper import scrape_pages
from extractor import structure_content
from insights import aggregate_insights
from exporter import export

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Web Scraper",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AI Web Scraper")
st.caption("Enter a natural language query and get structured data from the web.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    default_count = st.slider("Default result count (if not in query)", 1, 10, 5)
    show_content = st.toggle("Show full content", value=False)
    st.divider()
    st.markdown("**Example queries**")
    examples = [
        "top 5 blogs about startup fundraising",
        "3 articles about electric vehicles",
        "best guides on personal finance",
        "top 7 articles about machine learning trends",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=False):
            st.session_state["query_input"] = ex

# ── Query input ───────────────────────────────────────────────────────────────
query = st.text_input(
    "Your query",
    placeholder="e.g. top 5 blogs about startup fundraising",
    key="query_input"
)

run_btn = st.button("🚀 Run Scraper", type="primary", disabled=not query)

# ── Pipeline ──────────────────────────────────────────────────────────────────
if run_btn and query:
    search_query, n = parse_query(query)
    if n == 5:
        n = default_count

    st.info(f"Search query: **{search_query}** | Fetching **{n}** results")

    # Step 1: Search
    with st.status("🔎 Searching the web...", expanded=True) as status:
        search_results = search_web(search_query, max_results=n + 5)
        selected = search_results[:n]
        st.write(f"Found {len(search_results)} results, selected top {len(selected)}")
        for r in selected:
            st.write(f"- [{r['title']}]({r['url']})")
        status.update(label="✅ Search complete", state="complete")

    if not selected:
        st.error("No results found. Try a different query.")
        st.stop()

    # Step 2: Scrape
    with st.status("🌐 Scraping pages...", expanded=False) as status:
        urls = [r["url"] for r in selected]
        html_map = scrape_pages(urls)
        status.update(label="✅ Scraping complete", state="complete")

    # Step 3: Extract
    with st.status("🧠 Extracting & structuring content...", expanded=False) as status:
        search_meta_map = {r["url"]: r for r in selected}
        structured = []
        for url in urls:
            result = structure_content(url, html_map.get(url, ""), search_meta_map.get(url, {}))
            structured.append(result)
        status.update(label="✅ Extraction complete", state="complete")

    # Step 4: Insights
    insights = aggregate_insights(structured)

    # ── Export ────────────────────────────────────────────────────────────────
    json_path, csv_path = export(structured, search_query)

    # ── Results tabs ──────────────────────────────────────────────────────────
    st.divider()
    tab_results, tab_insights, tab_table, tab_export = st.tabs(
        ["📄 Results", "💡 Insights", "📊 Table View", "⬇️ Export"]
    )

    with tab_results:
        for i, r in enumerate(structured, 1):
            with st.expander(f"{i}. {r['title'] or r['url']}", expanded=(i == 1)):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"🔗 [{r['url']}]({r['url']})")
                    st.markdown(f"✍️ **Author:** {r['author'] or 'N/A'}  |  📅 **Date:** {r['publish_date'] or 'N/A'}")
                    st.markdown("**Summary**")
                    st.write(r["summary"] or "—")
                    if show_content and r.get("content"):
                        st.markdown("**Full Content**")
                        st.write(r["content"])
                with col2:
                    if r["key_points"]:
                        st.markdown("**Key Points**")
                        for kp in r["key_points"]:
                            st.markdown(f"• {kp}")
                    if r["topics"]:
                        st.markdown("**Topics**")
                        st.write(", ".join(r["topics"]))

    with tab_insights:
        st.subheader("Aggregated Insights")
        for line in insights:
            st.write(line)

    with tab_table:
        df = pd.DataFrame([
            {
                "Title": r["title"],
                "Website": r["website"],
                "Author": r["author"],
                "Date": r["publish_date"],
                "Summary": r["summary"],
                "Topics": ", ".join(r["topics"]),
            }
            for r in structured
        ])
        st.dataframe(df, width='stretch')

    with tab_export:
        st.success(f"Files saved to `output/` folder")

        # JSON download
        with open(json_path, "r", encoding="utf-8") as f:
            st.download_button(
                "⬇️ Download JSON",
                data=f.read(),
                file_name=os.path.basename(json_path),
                mime="application/json"
            )

        # CSV download
        with open(csv_path, "r", encoding="utf-8") as f:
            st.download_button(
                "⬇️ Download CSV",
                data=f.read(),
                file_name=os.path.basename(csv_path),
                mime="text/csv"
            )

        st.markdown("**Raw JSON**")
        st.json(structured)
