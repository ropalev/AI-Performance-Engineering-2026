import asyncio
import os

import httpx
from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from gihub import fetch_repo_tree, fetch_file_content
from helpers import parse_github_url, build_tree_text
from llm import call_llm


MAX_TOTAL_CHARS = int(os.environ.get("MAX_TOTAL_CHARS", "80000"))
MAX_FILE_CHARS = int(os.environ.get("MAX_FILE_CHARS", "8000"))
MAX_FILES = int(os.environ.get("MAX_FILES", "30"))
CONCURRENT_FETCHES = int(os.environ.get("CONCURRENT_FETCHES", "6"))


class SummarizeRequest(BaseModel):
    github_url: str

router = APIRouter()

@router.post("/summarize")
async def summarize(request: SummarizeRequest):
    owner, repo = parse_github_url(request.github_url)
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

    # 1. Fetch tree
    try:
        all_items, candidate_files = await fetch_repo_tree(owner, repo)
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Network error contacting GitHub: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"GitHub API error {exc.response.status_code}")

    if not all_items:
        raise HTTPException(status_code=404, detail="Repository is empty.")

    # 2. Build directory tree string
    dir_tree = build_tree_text(all_items)

    # 3. Fetch file contents concurrently (top candidates only)
    sem = asyncio.Semaphore(CONCURRENT_FETCHES)
    top_candidates = candidate_files[: MAX_FILES * 2]
    fetch_tasks = [fetch_file_content(owner, repo, item["path"], sem) for item in top_candidates]
    raw_results = await asyncio.gather(*fetch_tasks)

    selected: list[tuple[str, str]] = []
    total_chars = 0

    for path, content in raw_results:
        if content is None or total_chars >= MAX_TOTAL_CHARS:
            break
        if len(content) > MAX_FILE_CHARS:
            content = content[:MAX_FILE_CHARS] + "\n... [truncated]"
        selected.append((path, content))
        total_chars += len(content)
        if len(selected) >= MAX_FILES:
            break

    # 4. Build the files section for the prompt
    file_sections = "\n\n".join(f"--- {p} ---\n{c}" for p, c in selected)

    # 5. Call the LLM
    try:
        result = call_llm(owner, repo, dir_tree, file_sections)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM API error: {exc}")

    return {
        "summary": str(result.get("summary", "")),
        "technologies": list(result.get("technologies", [])),
        "structure": str(result.get("structure", "")),
    }


