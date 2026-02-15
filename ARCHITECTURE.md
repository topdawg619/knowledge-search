# Knowledge Search Architecture

## Overview
Knowledge Search is a fully client-side semantic search portal over our Obsidian research vault. The build pipeline ingests markdown notes, chunks and embeds them offline, stores the vectors in JSON, and serves a static UI (GitHub Pages) that runs similarity search entirely in-browser via WebAssembly models. No server-side API is involved, so the solution remains privacy-friendly and easy to host.

```
Vault Markdown ──▶ Chunker + Embedder (fastembed) ──▶ JSON Vector Index
                                               │
                                               └──▶ “public/data/index.json” (static asset)
Browser ▶ loads index + @xenova/transformers encoder ──▶ Cosine search + UI render
```

- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2` via `fastembed` during build, and via `@xenova/transformers` at runtime.
- **Storage:** flat JSON (`data/index.json`) containing text chunks, source paths, normalized embeddings.
- **Frontend:** vanilla JS (no React) served from GitHub Pages; fetches the JSON, loads the MiniLM encoder into WASM, embeds the query, and ranks results locally.

## Components
### 1. Ingestion & Index Build (`scripts/build_index.py`)
1. **File discovery:** glob markdown files under `research/ai-learning-library/**/*.md` and top-level `research/*.md`. Update `SOURCE_GLOBS` to include other folders.
2. **Chunking:** paragraphs grouped into ~600-character chunks with a minimum size of 180 chars. Oversized paragraphs are split; smaller fragments are merged for better semantic coherence.
3. **Embedding:** uses `fastembed.TextEmbedding` (MiniLM) to encode each chunk.
4. **Storage:** writes JSON with fields `{text, source, embedding, norm}` to `data/index.json` and mirrors it under `public/data/index.json` for easy serving.

Run manually: `python3 scripts/build_index.py`

### 2. Static Assets
- `index.html` – hero, search input, results pane.
- `styles.css` – minimal design system.
- `app.js` – loads the index, initializes the encoder, and performs cosine similarity.
- `public/data/index.json` – fetchable embedding store.

### 3. Frontend Flow (`app.js`)
1. Fetch `data/index.json`.
2. Lazy-load `@xenova/transformers` MiniLM encoder (quantized) and set status badge to “Ready.”
3. On search: embed the query, compute cosine similarity vs each entry’s vector using the stored norms, and display the top 8 results.
4. Each result links back to the source markdown in GitHub (`https://github.com/topdawg619/jarvis-dashboard/blob/main/<path>`).

### 4. Deployment
1. `git init` + push to GitHub (`topdawg619/knowledge-search`).
2. Enable GitHub Pages (branch `master`, path `/`). The `public/data/index.json` is bundled automatically.
3. Visit `https://topdawg619.github.io/knowledge-search/` – entire experience runs client-side.

## Refresh Workflow
1. Update markdown notes.
2. Run `python3 scripts/build_index.py` to re-chunk and embed.
3. Commit updated `data/index.json` + `public/data/index.json` (and any new assets).
4. Push to GitHub – Pages redeploys automatically.

## Next Steps / Enhancements
- Incremental chunking (only re-embed changed files).
- Multi-folder source selector + folder tagging/filtering in UI.
- Auth gating (Cloudflare Access, basic auth, or PAT gating).
- UI polishing: facet filters, pinned queries, offline caching.
- Observability: embed version, chunk stats, build timestamps.

This document lives beside the code (`projects/knowledge-search/ARCHITECTURE.md`) so future contributors can see the data flow and deployment mechanics at a glance.
