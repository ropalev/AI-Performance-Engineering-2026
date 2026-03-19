import asyncio
import base64
from typing import Optional

import httpx
from fastapi import HTTPException

from helpers import get_github_headers, file_priority, should_skip


async def fetch_repo_tree(owner: str, repo: str) -> tuple[list, list]:
    """Return (all_tree_items, filtered_and_sorted_blobs)."""
    headers = get_github_headers()

    async with httpx.AsyncClient(timeout=30) as client:
        repo_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
        )
        if repo_resp.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{owner}/{repo}' not found or is private.",
            )
        if repo_resp.status_code == 403:
            raise HTTPException(
                status_code=429,
                detail="GitHub API rate limit exceeded. Try again later.",
            )
        repo_resp.raise_for_status()

        default_branch = repo_resp.json().get("default_branch", "main")

        tree_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1",
            headers=headers,
        )
        tree_resp.raise_for_status()

    all_items = tree_resp.json().get("tree", [])
    blobs = [i for i in all_items if i["type"] == "blob" and not should_skip(i["path"])]
    blobs.sort(key=lambda x: file_priority(x["path"]))
    return all_items, blobs


async def fetch_file_content(
    owner: str, repo: str, path: str, sem: asyncio.Semaphore
) -> tuple[str, Optional[str]]:
    headers = get_github_headers()
    async with sem:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                    headers=headers,
                )
            if resp.status_code != 200:
                return path, None
            data = resp.json()
            if not isinstance(data, dict):
                return path, None
            if data.get("encoding") == "base64":
                raw = base64.b64decode(data["content"].replace("\n", ""))
                return path, raw.decode("utf-8", errors="replace")
            return path, data.get("content") or None
        except Exception:
            return path, None
