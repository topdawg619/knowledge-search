#!/usr/bin/env python3
"""Embed markdown notes into a JSON vector index for the knowledge search UI."""
from __future__ import annotations

import glob
import json
import math
from pathlib import Path
from typing import List, Tuple

from fastembed import TextEmbedding

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DATA_DIR = ROOT / "data"
PUBLIC_DATA_DIR = ROOT / "public" / "data"
for directory in (PRIVATE_DATA_DIR, PUBLIC_DATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = PRIVATE_DATA_DIR / "index.json"
PUBLIC_OUTPUT = PUBLIC_DATA_DIR / "index.json"

SOURCE_GLOBS = [
    ROOT.parent.parent / "research" / "ai-learning-library" / "**" / "*.md",
    ROOT.parent.parent / "research" / "*.md",
]

CHUNK_SIZE = 600  # characters
MIN_CHUNK = 180


def read_markdown_files() -> List[Tuple[Path, str]]:
    records: List[Tuple[Path, str]] = []
    for pattern in SOURCE_GLOBS:
        for path_str in glob.glob(str(pattern), recursive=True):
            file = Path(path_str)
            if file.is_file():
                try:
                    text = file.read_text(encoding="utf-8")
                except Exception as exc:  # noqa: BLE001
                    print(f"Skipping {file}: {exc}")
                    continue
                if text.strip():
                    records.append((file, text))
    return records


def chunk_text(text: str) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    buffer = ""
    for para in paragraphs:
        if len(buffer) + len(para) + 1 <= CHUNK_SIZE:
            buffer = f"{buffer}\n\n{para}".strip()
        else:
            if len(buffer) >= MIN_CHUNK:
                chunks.append(buffer)
            if len(para) > CHUNK_SIZE:
                start = 0
                while start < len(para):
                    end = min(len(para), start + CHUNK_SIZE)
                    segment = para[start:end].strip()
                    if len(segment) >= MIN_CHUNK:
                        chunks.append(segment)
                    start = end
                buffer = ""
            else:
                buffer = para
    if buffer and len(buffer) >= MIN_CHUNK:
        chunks.append(buffer)
    return chunks


def build_index():
    records = read_markdown_files()
    if not records:
        raise SystemExit("No markdown files found; adjust SOURCE_GLOBS.")

    embedder = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")

    entries = []
    for file, text in records:
        rel_path = file.relative_to(ROOT.parent.parent)
        chunks = chunk_text(text)
        if not chunks:
            continue
        embeddings = embedder.embed(chunks)
        for chunk, emb in zip(chunks, embeddings):
            emb_list = [round(float(x), 6) for x in emb]
            norm = round(math.sqrt(sum(v * v for v in emb_list)), 6)
            entries.append(
                {
                    "text": chunk,
                    "source": str(rel_path),
                    "embedding": emb_list,
                    "norm": norm,
                }
            )

    payload = json.dumps({"entries": entries}, ensure_ascii=False)
    OUTPUT_FILE.write_text(payload, encoding="utf-8")
    PUBLIC_OUTPUT.write_text(payload, encoding="utf-8")
    print(f"Wrote {len(entries)} chunks → {OUTPUT_FILE}")


if __name__ == "__main__":
    build_index()
