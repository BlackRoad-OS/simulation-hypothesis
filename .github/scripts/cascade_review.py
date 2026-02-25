#!/usr/bin/env python3
"""
Cascade PR review using multiple free GitHub Models agents.

Routes each pull request through two independent free-tier AI models
and writes a combined Markdown review to /tmp/cascade_review.md.

Cost: $0 — uses the GitHub Models free rate-limited tier.
Docs: https://docs.github.com/en/github-models/about-github-models
"""

import json
import os
import subprocess
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Configuration — free models only (no premium request multiplier cost)
# ---------------------------------------------------------------------------
MODELS = [
    {
        "id": "openai/gpt-4o-mini",
        "label": "Agent 1 · `openai/gpt-4o-mini`",
        "system": (
            "You are a concise code reviewer. Provide clear, actionable feedback "
            "focused on correctness, clarity, and potential issues."
        ),
    },
    {
        "id": "meta/meta-llama-3.1-8b-instruct",
        "label": "Agent 2 · `meta/meta-llama-3.1-8b-instruct`",
        "system": (
            "You are a thoughtful code reviewer. Focus on logic, edge cases, "
            "and documentation quality."
        ),
    },
]

MODELS_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"
MAX_DIFF_CHARS = 6000   # stay well within free-tier token limits
MAX_TOKENS = 512
TEMPERATURE = 0.3
OUTPUT_FILE = "/tmp/cascade_review.md"


def get_pr_diff(pr_number: str, repo: str) -> str:
    """Fetch the PR diff using the GitHub CLI."""
    try:
        result = subprocess.run(
            ["gh", "pr", "diff", pr_number, "--repo", repo],
            capture_output=True,
            text=True,
            timeout=30,
        )
        diff = result.stdout or ""
        return diff[:MAX_DIFF_CHARS]
    except Exception as exc:
        return f"(diff unavailable: {exc})"


def call_model(model_id: str, system_prompt: str, user_prompt: str, token: str) -> str:
    """Call one GitHub Models endpoint and return the reply text."""
    payload = json.dumps(
        {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
        }
    ).encode()

    req = urllib.request.Request(
        MODELS_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        return f"*(model unavailable — HTTP {exc.code}: {body[:200]})*"
    except Exception as exc:
        return f"*(model unavailable — {exc})*"


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", "")
    pr_number = os.environ.get("PR_NUMBER", "")
    pr_title = os.environ.get("PR_TITLE", "(no title)")
    pr_body = os.environ.get("PR_BODY", "")[:1000]
    repo = os.environ.get("REPO", "")

    diff = get_pr_diff(pr_number, repo)

    user_prompt = (
        f"**PR title:** {pr_title}\n\n"
        f"**PR description:**\n{pr_body}\n\n"
        f"**Diff (may be truncated):**\n```diff\n{diff}\n```\n\n"
        "Please provide 3–5 bullet points of review feedback."
    )

    sections: list[str] = []
    for model in MODELS:
        reply = call_model(model["id"], model["system"], user_prompt, token)
        sections.append(f"### {model['label']}\n\n{reply}")

    body = "\n\n---\n\n".join(sections)
    comment = (
        "## 🤖 Cascade Review — Multiple Free Agents ($0)\n\n"
        "Two independent AI agents reviewed this pull request using the "
        "[GitHub Models free tier](https://docs.github.com/en/github-models/about-github-models).\n\n"
        "---\n\n"
        f"{body}\n\n"
        "---\n\n"
        "*Cost: $0 — both models used within the GitHub Models free rate-limited tier.*"
    )

    with open(OUTPUT_FILE, "w") as fh:
        fh.write(comment)

    print(f"Review written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
