# Knowledge Search FAQ

## 1. How do I rebuild the semantic index?
1. Ensure Python 3.10+ and `fastembed` are installed.
2. From `projects/knowledge-search/`, run `python3 scripts/build_index.py`.
3. The script scans markdown sources (`research/ai-learning-library/**`, `research/*.md`), chunks them, embeds with MiniLM, and writes `data/index.json` + `public/data/index.json`.
4. Spot-check the JSON (size + sample entries), then commit/push both files alongside any UI changes.
5. GitHub Pages will redeploy automatically.

## 2. How do I include more folders (e.g., project docs)?
- Edit `SOURCE_GLOBS` inside `scripts/build_index.py` and add new patterns, e.g.:
  ```python
  SOURCE_GLOBS = [
      ROOT.parent.parent / "research" / "ai-learning-library" / "**" / "*.md",
      ROOT.parent.parent / "projects" / "**" / "*.md",
  ]
  ```
- Rerun the build script to pull the new files into the index.

## 3. The browser shows “Failed to load index/model.” What now?
| Symptom | Fix |
| --- | --- |
| `data/index.json` returns 404 | Confirm both `data/index.json` and `public/data/index.json` exist in the repo; if hosting from a subdirectory, update the fetch path in `app.js`. |
| Encoder never finishes loading | Ensure the site is served over HTTPS (required for WASM). Check the browser console for CORS/network errors. If offline, pre-cache the model by loading once with network access. |
| Query returns instantly but no results | The JSON may be empty/stale; rerun `scripts/build_index.py` and redeploy. |

## 4. How do I refresh GitHub Pages once the index changes?
1. Rebuild the index locally (`python3 scripts/build_index.py`).
2. Commit and push changes to GitHub.
3. Monitor the Pages deploy tab for the latest build (should turn green). If it fails, inspect the logs.
4. Reload `https://topdawg619.github.io/knowledge-search/` and verify the status flips to “Ready” and new content appears.

## 5. Can we host the JSON/model somewhere else (CDN, private bucket)?
- Yes. Update `app.js` to point to the new URL (set `const DATA_URL = 'https://...'`).
- If hosting a private dataset, consider gating access with Cloudflare Access or requiring user-supplied tokens before fetching.

## 6. How do I troubleshoot local previews?
- Serve via `python3 -m http.server` from the project root so relative paths resolve (`data/index.json`).
- Clear the browser cache if the index was updated but results look stale.
- Use devtools network tab to confirm the JSON and wasm files were fetched (200 response).
