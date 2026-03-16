"""
exporter.py - Export structured results to JSON and CSV
"""
import json
import csv
import os
from datetime import datetime


def export(results: list[dict], query: str, output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = query.replace(" ", "_")[:40]
    base = os.path.join(output_dir, f"{slug}_{timestamp}")

    # JSON
    json_path = base + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # CSV (flatten key_points and topics to strings)
    csv_path = base + ".csv"
    if results:
        fieldnames = ["website", "url", "title", "author", "publish_date", "content", "summary", "key_points", "topics"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                row = dict(r)
                row["key_points"] = " | ".join(r.get("key_points", []))
                row["topics"] = ", ".join(r.get("topics", []))
                writer.writerow({k: row.get(k, "") for k in fieldnames})

    return json_path, csv_path
