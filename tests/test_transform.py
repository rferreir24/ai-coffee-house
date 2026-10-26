from ai_coffee_house import transform


def hit(title, url="https://example.com", points=10, object_id="1"):
    return {"objectID": object_id, "title": title, "url": url, "points": points, "num_comments": 3}


def test_ai_filter_keeps_ai_titles():
    assert transform.is_ai_story({"title": "New LLM beats GPT on coding"})
    assert transform.is_ai_story({"title": "How we use Claude in production"})


def test_ai_filter_drops_non_ai_and_partial_words():
    assert not transform.is_ai_story({"title": "Real estate tips for first-time buyers"})
    assert not transform.is_ai_story({"title": "He said the rain would stop"})  # "ai" inside "said"/"rain"


def test_security_tag():
    assert transform.is_security_story({"title": "Prompt injection hijacks an AI agent"})
    assert not transform.is_security_story({"title": "A new open-weights AI model"})


def test_ask_hn_without_url_links_to_discussion():
    story = transform.clean_story({"objectID": "42", "title": "Ask HN: AI?", "points": 5, "num_comments": 1})
    assert story["url"] == "https://news.ycombinator.com/item?id=42"


def test_build_stories_splits_filters_tags_and_ranks():
    hits = [
        hit("A small AI model", points=50, object_id="1"),
        hit("AI jailbreak found", points=300, object_id="2"),
        hit("Gardening for beginners", points=999, object_id="3"),
        hit("Attention paper", url="https://arxiv.org/abs/2410.12345", points=200, object_id="4"),
    ]
    stories, arxiv_posts = transform.build_stories(hits)
    assert [s["id"] for s in stories] == ["2", "1"]  # AI only, ranked by points
    assert stories[0]["security"] is True
    assert stories[1]["security"] is False
    assert [p["id"] for p in arxiv_posts] == ["4"]  # arXiv posts never appear in stories


def test_brand_names_match_with_version_numbers():
    assert transform.is_ai_story({"title": "Five Qwen3.8-27B models match"})
    assert transform.is_ai_story({"title": "Progressive disclosure in agents"})
