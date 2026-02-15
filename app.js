import { pipeline } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.6.1';

const statusEl = document.getElementById('status');
const queryInput = document.getElementById('query');
const searchBtn = document.getElementById('searchBtn');
const resultsEl = document.getElementById('results');

const REPO_BASE = 'https://github.com/topdawg619/jarvis-dashboard/blob/main/';
let entries = [];
let encoder = null;
let loading = false;

async function loadIndex() {
  const res = await fetch('data/index.json');
  if (!res.ok) {
    throw new Error('Unable to load index');
  }
  const json = await res.json();
  entries = json.entries || [];
}

async function initEncoder() {
  encoder = await pipeline('feature-extraction', 'sentence-transformers/all-MiniLM-L6-v2', { quantized: true });
}

function cosineSimilarity(a, aNorm, b, bNorm) {
  let dot = 0;
  for (let i = 0; i < b.length; i += 1) {
    dot += a[i] * b[i];
  }
  return dot / (aNorm * bNorm);
}

async function embedQuery(text) {
  const output = await encoder(text, { pooling: 'mean', normalize: true });
  const data = Array.from(output.data);
  let norm = 0;
  for (const val of data) {
    norm += val * val;
  }
  return { vector: data, norm: Math.sqrt(norm) };
}

async function performSearch() {
  const query = queryInput.value.trim();
  if (!query) {
    resultsEl.innerHTML = '<p class="muted">Type a question to search the vault.</p>';
    return;
  }
  if (loading) return;
  loading = true;
  statusEl.textContent = 'Searching…';
  try {
    const { vector, norm } = await embedQuery(query);
    const scored = entries
      .map((entry) => {
        const score = cosineSimilarity(vector, norm, entry.embedding, entry.norm || 1);
        return { ...entry, score };
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 8);
    if (!scored.length) {
      resultsEl.innerHTML = '<p>No matches yet.</p>';
    } else {
      resultsEl.innerHTML = scored
        .map(
          (entry) => `
          <article class="result">
            <small><a href="${REPO_BASE}${entry.source}" target="_blank" rel="noopener">${entry.source}</a></small>
            <pre>${entry.text}</pre>
            <span class="score">Relevance: ${(entry.score * 100).toFixed(1)}%</span>
          </article>`
        )
        .join('');
    }
  } catch (err) {
    console.error(err);
    resultsEl.innerHTML = `<p class="error">${err.message}</p>`;
  } finally {
    statusEl.textContent = 'Ready';
    loading = false;
  }
}

async function init() {
  try {
    await loadIndex();
    statusEl.textContent = 'Loading encoder…';
    await initEncoder();
    statusEl.textContent = 'Ready';
  } catch (err) {
    console.error(err);
    statusEl.textContent = 'Failed to load index/model';
  }
}

searchBtn.addEventListener('click', performSearch);
queryInput.addEventListener('keydown', (evt) => {
  if (evt.key === 'Enter') {
    performSearch();
  }
});

init();
