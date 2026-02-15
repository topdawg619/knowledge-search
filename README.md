# Agentra Knowledge Search

Static semantic-search dashboard for the internal AI knowledge base. It embeds the Obsidian vault notes offline and serves a browser UI (React-free, pure JS) that runs the same `sentence-transformers/all-MiniLM-L6-v2` encoder via `@xenova/transformers` on-device. No back-end required, so it can live on GitHub Pages.

## Structure
```
projects/knowledge-search/
├── index.html        # UI shell
├── styles.css        # glassmorphism styling
├── app.js            # loads embeddings + runs similarity search in-browser
├── data/index.json   # vector store produced by build script (committed)
└── scripts/build_index.py  # regenerates embeddings from markdown sources
```

## Building / Updating
1. Ensure `fastembed` is installed (`pip install fastembed`).
2. From `projects/knowledge-search/`, run:
   ```bash
   python3 scripts/build_index.py
   ```
   This scans `research/ai-learning-library/**.md` (and top-level `research/*.md`), chunks the text, generates embeddings, and writes `data/index.json` (and mirrors it to `public/data/index.json` for GitHub Pages).
3. Commit the updated `data/index.json` along with any UI changes, push to GitHub, and Pages will refresh automatically.

## Usage
- Open the deployed page, wait for the “Ready” status.
- Type a natural-language question (e.g., “LoRA vs QLoRA cost tradeoffs on Azure”), hit Enter.
- Results show the top matching snippets with file names and relevance scores. Clicking a source path opens the raw markdown (future enhancement: direct links into the vault repo).

## Notes
- Uses `sentence-transformers/all-MiniLM-L6-v2` for compact 384-dim embeddings (fast to load in-browser).
- Because everything runs locally (no server), the dataset stays public-safe; redact before pushing.
- Extend `SOURCE_GLOBS` inside `build_index.py` to cover other folders (e.g., `projects/`, `docs/`).
