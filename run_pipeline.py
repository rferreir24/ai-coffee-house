"""Run the AI Coffee House ETL pipeline: Extract -> Transform -> Load."""

import sys
from datetime import datetime, timezone

from ai_coffee_house import extract, load, transform

DOCS = "docs"
TEMPLATE = "templates/index.html.j2"


def main():
    # EXTRACT
    try:
        hits = extract.fetch_hn_stories(days=7, min_points=20)
    except Exception as error:
        print(f"Could not reach Hacker News ({error}). Keeping the last good page.")
        sys.exit(1)
    if not hits:
        print("Hacker News returned no stories. Keeping the last good page.")
        sys.exit(1)

    # TRANSFORM
    stories, arxiv_posts = transform.build_stories(hits)
    papers = []

    # LOAD
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stories": stories,
        "papers": papers,
    }
    load.write_json(data, f"{DOCS}/data.json")
    load.render_page(data, TEMPLATE, f"{DOCS}/index.html")

    security = sum(1 for s in stories if s["security"])
    print(f"{len(hits)} stories fetched")
    print(f"  -> {len(stories)} AI stories ({security} security)")
    print(f"  -> {len(arxiv_posts)} posts link arXiv")
    print(f"Wrote {DOCS}/data.json and {DOCS}/index.html")


if __name__ == "__main__":
    main()
