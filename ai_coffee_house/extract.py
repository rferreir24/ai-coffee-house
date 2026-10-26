"""EXTRACT: pull raw data from the outside world (HN via Algolia, arXiv)."""

import time

import requests

ALGOLIA_URL = "https://hn.algolia.com/api/v1/search_by_date"


def fetch_hn_stories(days=7, min_points=20):
    """Return raw Algolia hits for stories from the last `days` days with `min_points`+ points."""
    since = int(time.time()) - days * 24 * 60 * 60
    hits = []
    page = 0
    while page < 10:  # safety cap
        response = requests.get(
            ALGOLIA_URL,
            params={
                "tags": "story",
                "numericFilters": f"created_at_i>{since},points>={min_points}",
                "hitsPerPage": 1000,
                "page": page,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        hits.extend(data["hits"])
        page += 1
        if page >= data["nbPages"]:
            break
    return hits
