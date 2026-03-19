
import json
import os
import re

from fastapi import HTTPException
from openai import OpenAI

PROVIDERS = {
    "nebius": {
        "base_url": "https://api.studio.nebius.ai/v1/",
        "api_key_env": "NEBIUS_API_KEY",
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
    },
}


def get_llm_client() -> tuple[OpenAI, str]:
    provider_name = os.environ.get("LLM_PROVIDER", "nebius").lower()
    provider = PROVIDERS.get(provider_name)
    if not provider:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown LLM_PROVIDER '{provider_name}'. Choose from: {', '.join(PROVIDERS)}.",
        )

    api_key = os.environ.get(provider["api_key_env"])
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=f"{provider['api_key_env']} environment variable is not set.",
        )

    model = os.environ.get("LLM_MODEL") or provider["model"]
    client = OpenAI(api_key=api_key, base_url=provider["base_url"])
    return client, model


def call_llm(owner: str, repo: str, dir_tree: str, file_sections: str) -> dict:
    client, model = get_llm_client()

    prompt = f"""You are analyzing the GitHub repository: {owner}/{repo}

## Directory Structure
```
{dir_tree}
```

## Key File Contents

{file_sections}

Based on the above, respond with a JSON object containing exactly these three fields:
{{
  "summary": "2-4 sentence human-readable description of what this project does and its main purpose",
  "technologies": ["list", "of", "technologies", "languages", "and", "frameworks", "used"],
  "structure": "1-3 sentence description of how the project is organized (key directories, layout pattern)"
}}

Return ONLY the JSON object — no markdown, no extra text."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a software analyst. Analyze code repositories and return "
                    "concise, accurate structured summaries as valid JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=800,
    )

    result_text = response.choices[0].message.content.strip()

    if "```json" in result_text:
        result_text = result_text.split("```json", 1)[1].rsplit("```", 1)[0].strip()
    elif result_text.startswith("```"):
        result_text = result_text.split("```", 1)[1].rsplit("```", 1)[0].strip()

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", result_text, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise HTTPException(status_code=500, detail="LLM returned non-JSON output.")
