"""LOAD: save the transformed data as JSON and as the finished web page."""

import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def write_json(data, path):
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def brewed_at(iso_time):
    """'2026-10-26T18:00:00+00:00' -> 'Oct 26, 18:00 UTC'"""
    return datetime.fromisoformat(iso_time).strftime("%b %d, %H:%M UTC")


def render_page(data, template_path, path):
    template_path = Path(template_path)
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(["html", "j2"]),
    )
    template = env.get_template(template_path.name)
    html = template.render(
        stories=data["stories"],
        papers=data["papers"],
        brewed_at=brewed_at(data["generated_at"]),
    )
    Path(path).write_text(html, encoding="utf-8")
