# ☕ AI Coffee House

A cute, 8-bit page that cuts through AI noise. It shows **this week's AI stories getting the most engagement on Hacker News**, plus the **arXiv papers HN is talking about**, so you can see when research hits the mainstream.

**Live site:** https://rferreir24.github.io/ai-coffee-house/

## How it works: a simple ETL pipeline

```
EXTRACT                     TRANSFORM                                   LOAD
HN Search API (Algolia) →   split arXiv links from other stories    →   docs/data.json
  this week's stories,      stories: keep AI keywords, tag security     docs/index.html
  20+ points                papers:  dedupe, look up arXiv (Atom feed),  (8-bit template)
                                     keep AI categories
                            rank everything by HN points
```

- `ai_coffee_house/extract.py`: calls the HN Search API (Algolia) and the arXiv API
- `ai_coffee_house/transform.py`: pure functions that clean, split, filter, tag, dedupe, and rank
- `ai_coffee_house/keywords.py`: the AI and security keyword lists, and the AI arXiv categories (tune these!)
- `ai_coffee_house/load.py`: writes `docs/data.json` and renders `templates/index.html.j2` into `docs/index.html`
- `run_pipeline.py`: runs extract → transform → load and prints a summary

GitHub Pages serves the `docs/` folder.

## Run it

```
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
```

Then open `docs/index.html` in a browser. Run the tests with `pytest`.

No API keys needed. Both APIs are free and public.

## Credits

- Color palette: [Benten Pond](https://lospec.com/palette-list/benten-pond) by [Terry Ross](https://lospec.com/cutegamesclub), via [Lospec](https://lospec.com)
- Fonts: [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) and [VT323](https://fonts.google.com/specimen/VT323) from Google Fonts
- Data: [Hacker News Search API (Algolia)](https://hn.algolia.com/api) and the [arXiv API](https://info.arxiv.org/help/api/)

Built using the skills from Devpost's Build With AI: Basics hackathon.
