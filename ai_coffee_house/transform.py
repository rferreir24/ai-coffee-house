"""TRANSFORM: turn raw data into exactly what the page needs.

Every function here is pure: data in, data out, no network calls. That makes them easy to test.
"""

import re

from ai_coffee_house.keywords import AI_CATEGORIES, AI_KEYWORDS, SECURITY_KEYWORDS

HN_ITEM_URL = "https://news.ycombinator.com/item?id="


def _matches_any(text, keywords):
    """True if any keyword appears in text as a whole word or phrase (case-insensitive).

    A number may follow the keyword, so "qwen" matches "Qwen3.8" but "ai" doesn't match "said".
    """
    text = text.lower()
    for keyword in keywords:
        if re.search(r"(?<!\w)" + re.escape(keyword.lower()) + r"(?![a-z_])", text):
            return True
    return False


def clean_story(hit):
    """Keep only the fields we use, and build the HN discussion link."""
    hn_url = HN_ITEM_URL + hit["objectID"]
    return {
        "id": hit["objectID"],
        "title": hit.get("title") or "",
        "url": hit.get("url") or hn_url,  # Ask HN posts have no url
        "points": hit.get("points") or 0,
        "comments": hit.get("num_comments") or 0,
        "hn_url": hn_url,
        "created_at": hit.get("created_at"),
    }


def is_arxiv_url(url):
    return "arxiv.org/" in url.lower()


def split_arxiv(stories):
    """Split stories into (posts linking arXiv, everything else)."""
    papers = [s for s in stories if is_arxiv_url(s["url"])]
    others = [s for s in stories if not is_arxiv_url(s["url"])]
    return papers, others


def is_ai_story(story):
    return _matches_any(story["title"], AI_KEYWORDS)


def is_security_story(story):
    return _matches_any(story["title"], SECURITY_KEYWORDS)


def rank(items):
    """Sort by points, highest first."""
    return sorted(items, key=lambda item: item["points"], reverse=True)


def build_stories(hits):
    """Run the full story transform: clean -> split -> filter AI -> tag security -> rank.

    Returns (ai_stories, arxiv_posts) so papers can be handled separately.
    """
    cleaned = [clean_story(hit) for hit in hits]
    arxiv_posts, others = split_arxiv(cleaned)
    ai_stories = [s for s in others if is_ai_story(s)]
    for story in ai_stories:
        story["security"] = is_security_story(story)
    return rank(ai_stories), arxiv_posts


ARXIV_ID_PATTERN = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})")


def arxiv_id_from_url(url):
    """'https://arxiv.org/pdf/2410.12345v2' -> '2410.12345'. None if there's no paper ID."""
    match = ARXIV_ID_PATTERN.search(url)
    return match.group(1) if match else None


def dedupe_papers(posts):
    """One entry per paper, keeping the HN post with the most points."""
    best = {}
    for post in posts:
        arxiv_id = arxiv_id_from_url(post["url"])
        if arxiv_id is None:
            continue
        if arxiv_id not in best or post["points"] > best[arxiv_id]["points"]:
            best[arxiv_id] = {**post, "arxiv_id": arxiv_id}
    return list(best.values())


def is_ai_paper(categories):
    return any(category in AI_CATEGORIES for category in categories)


def build_papers(posts, arxiv_info):
    """Attach arXiv titles and categories, keep AI papers only, and rank by HN points."""
    papers = []
    for post in posts:
        info = arxiv_info.get(post["arxiv_id"])
        if info is None or not is_ai_paper(info["categories"]):
            continue
        papers.append({
            "arxiv_id": post["arxiv_id"],
            "title": info["title"],
            "arxiv_url": "https://arxiv.org/abs/" + post["arxiv_id"],
            "categories": info["categories"],
            "points": post["points"],
            "comments": post["comments"],
            "hn_url": post["hn_url"],
        })
    return rank(papers)
