"""
insights.py - Cross-source theme and insight aggregation
"""
from collections import Counter


def aggregate_insights(structured_results: list[dict]) -> list[str]:
    """
    Find recurring topics and key points across all sources.
    Returns a list of shared insight strings.
    """
    topic_counter = Counter()
    all_key_points = []

    for r in structured_results:
        for topic in r.get("topics", []):
            topic_counter[topic] += 1
        all_key_points.extend(r.get("key_points", []))

    # Topics mentioned in 2+ sources
    common_topics = [t for t, count in topic_counter.items() if count >= 2]

    insights = []

    if common_topics:
        insights.append(
            f"Common themes across sources: {', '.join(common_topics[:8])}"
        )

    # Deduplicate key points by rough similarity (first word match)
    seen_starts = set()
    unique_points = []
    for point in all_key_points:
        start = " ".join(point.lower().split()[:4])
        if start not in seen_starts:
            seen_starts.add(start)
            unique_points.append(point)

    if unique_points:
        insights.append("Recurring recommendations and insights:")
        insights.extend([f"  • {p}" for p in unique_points[:8]])

    return insights if insights else ["No strong cross-source patterns detected."]
