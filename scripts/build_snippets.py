#!/usr/bin/env python3
"""Generate concise snippets for the knowledge search index."""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "snippets.json"
PUBLIC_OUTPUT = ROOT / "public" / "data" / "snippets.json"

SOURCE_GLOBS = [
    ROOT.parent.parent / "research" / "ai-learning-library" / "**" / "*.md",
    ROOT.parent.parent / "research" / "*.md",
]

SUMMARY_SENTENCES = 2


def clean_markdown(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"#+ ", "", text)
    return text.strip()


def summarize(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = " ".join(sentences[:SUMMARY_SENTENCES]).strip()
    return summary or text[:280]


def build_snippets():
    entries = []
    for pattern in SOURCE_GLOBS:
        for path_str in glob.glob(str(pattern), recursive=True):
            file = Path(path_str)
            if not file.is_file():
                continue
            try:
                text = file.read_text(encoding="utf-8")
            except Exception:
                continue
            cleaned = clean_markdown(text)
            if not cleaned:
                continue
            title = file.stem.replace('-', ' ').title()
            entries.append(
                {
                    "title": title,
                    "path": str(file.relative_to(ROOT.parent.parent)),
                    "snippet": summarize(cleaned),
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"documents": entries}, ensure_ascii=False), encoding="utf-8")
    PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_OUTPUT.write_text(json.dumps({"documents": entries}, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(entries)} snippets")


if __name__ == "__main__":
    build_snippets()
