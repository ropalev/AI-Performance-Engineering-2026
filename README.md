# GitHub Repository Summarizer

Paste a GitHub repository URL — get back a plain-English summary of what the project does, what technologies it uses, and how the code is organized.

## Getting started

### 1. You need Python 3.10+

Check your version: `python --version`

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Create a `.env` file in the project root with the following content:

```
# --- LLM provider ---
LLM_PROVIDER = "nebius"   # nebius | groq

NEBIUS_API_KEY = ""       # https://studio.nebius.ai/
GROQ_API_KEY = ""         # https://console.groq.com/

# --- GitHub ---
GITHUB_TOKEN = ""         # https://github.com/settings/tokens (60 → 5000 req/hour)

# --- Limits ---
MAX_TOTAL_CHARS = 35000   # total characters sent to the LLM (~8k tokens)
MAX_FILE_CHARS = 4000     # max characters read from a single file
MAX_FILES = 30            # max number of files to include
CONCURRENT_FETCHES = 6    # parallel GitHub API requests
```

Fill in the key for the provider you chose. `GITHUB_TOKEN` is required — without it GitHub blocks you at 60 requests/hour, which isn't enough for most repos.

### 5. Start the server

```bash
python main.py
```

The server runs at `http://localhost:8000`.

### 6. Try it out

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/psf/requests"}'
```

You'll get something like:

```json
{
  "summary": "Requests is a popular Python HTTP library...",
  "technologies": ["Python", "urllib3", "certifi"],
  "structure": "Source code lives in src/requests/, tests in tests/, docs in docs/."
}
```

## How it works

### What gets sent to the LLM

The service doesn't download the entire repo — that would be slow and expensive. Instead it picks the most useful parts:

1. **File tree** — always included, gives the LLM an overview of the project layout.
2. **README** — top priority if one exists.
3. **Config and manifest files** — `package.json`, `pyproject.toml`, `requirements.txt`, etc. Instantly reveals the tech stack.
4. **Entry points** — `main.py`, `app.py`, `index.ts`, and similar. Files where execution begins.
5. **Other source files** — sorted by depth, shallower files first (they tend to be more central).

### What gets skipped

- Images, fonts, archives, compiled binaries
- Lock files (`package-lock.json`, `poetry.lock`, etc.) — huge and carry no semantic value
- Build and cache folders (`dist/`, `build/`, `__pycache__/`)
- Dependency folders (`node_modules/`, `.venv/`, `vendor/`)
- Minified files (`*.min.js`, `*.min.css`)

### Limits

To keep token usage reasonable, the service caps what it sends (all configurable in `.env`):

| Setting | Default | What it limits |
|---|---|---|
| `MAX_FILES` | 30 | number of files |
| `MAX_FILE_CHARS` | 4 000 | characters per file |
| `MAX_TOTAL_CHARS` | 35 000 | characters total (~8k tokens) |

Files are sorted by priority before the budget is applied, so the most useful content always makes the cut.

### Error responses

All errors come back in the same shape:

```json
{"status": "error", "message": "..."}
```

| Code | Reason |
|---|---|
| 400 | Not a valid GitHub URL |
| 404 | Repository doesn't exist or is private |
| 429 | GitHub API rate limit hit |
| 500 | API key not set |
| 502 | Network error or LLM API failure |

## Model choice

You can override the default model via `LLM_MODEL` in `.env`:

```
LLM_MODEL = "your-model-name"
```

If not set, the provider's default is used.

### Nebius — `meta-llama/Meta-Llama-3.1-70B-Instruct`

This model consistently returns clean JSON without extra text — which matters here because the output goes straight into a parser. Smaller models in the same family tend to add commentary or miss fields. 70B is the minimum size that handles code analysis reliably.

### Groq — `llama-3.3-70b-versatile`

Same model family, latest version available on Groq. The `versatile` variant handles a mix of code, config files, and prose better than `instant`, which is faster but cuts corners on output quality. The downside is the 12 000 TPM cap on the free tier — that's why `MAX_TOTAL_CHARS` defaults to 35 000 instead of the full 80 000.
