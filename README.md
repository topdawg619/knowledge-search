# Agentra Knowledge Search

Static semantic-search dashboard for the internal AI knowledge base. It embeds the Obsidian vault notes offline and serves a browser UI (React-free, pure JS) that runs the same `sentence-transformers/all-MiniLM-L6-v2` encoder via `@xenova/transformers` on-device. No back-end required, so it can live on GitHub Pages.

## Structure
```
projects/knowledge-search/
├── index.html        # UI shell
├── styles.css        # glassmorphism styling
├── app.js            # loads embeddings + runs similarity search in-browser
├── data/index.json   # vector store produced by build script (committed)
├── public/data/index.json  # copy served by GitHub Pages
└── scripts/build_index.py  # regenerates embeddings from markdown sources
```

## Prerequisites
- Python 3.10+
- `pip`
- `fastembed` Python package (installed below)

## Installation / Setup
1. **(Optional) virtualenv**
   ```bash
   cd projects/knowledge-search
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install build dependency**
   ```bash
   pip install fastembed
   ```
3. *(Optional)* freeze deps:
   ```bash
   pip freeze > requirements.txt
   ```

## Build / Update the Index
1. Ensure markdown sources under `research/ai-learning-library/**` (and `research/*.md`) are up to date.
2. Run the build script:
   ```bash
   python3 scripts/build_index.py
   ```
   - Scans markdown directories defined in `SOURCE_GLOBS`
   - Chunks content (~600 chars) and embeds via `fastembed`
   - Writes `data/index.json` and mirrors to `public/data/index.json`
3. Spot-check the JSON size/content, then commit both files along with UI changes.

## Local Preview
- No bundler required. Open `index.html` directly or run `python3 -m http.server 4173` inside this folder and browse `http://localhost:4173`.

## Deployment (GitHub Pages)
1. Commit + push to GitHub (`topdawg619/knowledge-search`).
2. In GitHub → Settings → Pages, publish from `master` / root (or `/` path). Pages will serve the static assets, including `public/data/index.json`.
3. Visit `https://topdawg619.github.io/knowledge-search/` and confirm the status badge flips to “Ready” after the encoder loads.

## Usage
1. Wait for “Ready.”
2. Type a natural-language query (e.g., “LoRA vs QLoRA on Azure”).
3. Results show snippets + source paths; clicking a path opens the markdown in GitHub.

## Troubleshooting
| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: fastembed` | Dependency missing in current venv. | Run `pip install fastembed` (activate venv first). |
| `No markdown files found; adjust SOURCE_GLOBS.` | Paths changed or directories absent. | Update `SOURCE_GLOBS` in `scripts/build_index.py` to point to the correct folders. |
| Browser fetches `data/index.json` but 404s | JSON not committed or path mismatch. | Ensure both `data/index.json` and `public/data/index.json` exist, commit them, and adjust fetch path in `app.js` if hosting in a subdirectory. |
| Search results stale/missing updates | Index wasn’t rebuilt after content changes. | Re-run `python3 scripts/build_index.py`, commit/push refreshed JSON. |
| Encoder never leaves “Loading…” | Browser blocked WASM fetch or offline. | Check console for CORS/network errors, ensure the site is served over HTTPS, retry once connection is stable. |

## Roadmap / Enhancements
- Incremental sync (only re-embed changed files)
- Multi-folder selection + folder filters in UI
- Auth gating (Cloudflare Access, PAT gating, basic auth proxy)
- UI polish: facets, saved queries, offline caching
- Observability: chunk stats, embedding version, build timestamps

Refer to `ARCHITECTURE.md` for the end-to-end pipeline and component detail.
