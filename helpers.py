import os
import re
from typing import Optional

from rules import SKIP_DIRS, SKIP_FILENAMES, SKIP_EXTENSIONS, ALLOWED_HIDDEN, PRIORITY_MAP, SOURCE_EXTS, CONFIG_EXTS


def parse_github_url(url: str) -> tuple[Optional[str], Optional[str]]:
    match = re.search(
        r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:[/?#].*)?$",
        url,
    )
    if not match:
        return None, None
    return match.group(1), match.group(2)


def should_skip(path: str) -> bool:
    parts = path.split("/")
    filename = parts[-1].lower()

    for part in parts[:-1]:
        if part.lower() in SKIP_DIRS:
            return True
        if part.startswith(".") and part != ".github":
            return True

    if filename in SKIP_FILENAMES:
        return True

    ext = os.path.splitext(filename)[1]
    if ext in SKIP_EXTENSIONS:
        return True

    if filename.endswith(".min.js") or filename.endswith(".min.css"):
        return True

    if filename.startswith(".") and filename not in ALLOWED_HIDDEN:
        return True

    return False


def file_priority(path: str) -> int:
    parts = path.split("/")
    filename = parts[-1].lower()
    depth = len(parts) - 1

    if filename in PRIORITY_MAP:
        return PRIORITY_MAP[filename]

    ext = os.path.splitext(filename)[1]
    if ext in SOURCE_EXTS:
        return 10 + depth
    if ext in CONFIG_EXTS:
        return 15 + depth
    return 20 + depth


def build_tree_text(items: list) -> str:
    dirs_added: set[str] = set()
    lines: list[str] = []

    for item in sorted(items, key=lambda x: x["path"]):
        parts = item["path"].split("/")
        for depth, part in enumerate(parts[:-1]):
            dir_path = "/".join(parts[: depth + 1])
            if dir_path not in dirs_added:
                dirs_added.add(dir_path)
                lines.append("  " * depth + part + "/")
        if item["type"] == "blob":
            lines.append("  " * (len(parts) - 1) + parts[-1])

    return "\n".join(lines[:400])


def get_github_headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not set. "
            "Without it GitHub allows only 60 requests/hour, which is not enough. "
            "Get a free token at https://github.com/settings/tokens and add it to .env"
        )
    return {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
    }