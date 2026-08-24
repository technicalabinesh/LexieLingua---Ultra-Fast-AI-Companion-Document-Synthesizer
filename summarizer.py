"""
Document Summarizer module.
"""

import os
import re
from openai import AzureOpenAI
from utils import extractive_summary, key_points, word_count

def _clean_base_url(url: str) -> str:
    match = re.match(r"^(https?://[^/]+)", url.strip())
    return match.group(1) if match else url.strip().rstrip("/")

def is_ai_mode_available() -> bool:
    return bool(
        os.getenv("AZURE_OPENAI_API_KEY")
        and os.getenv("AZURE_OPENAI_ENDPOINT")
        and os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )

def summarize_offline(text: str, length: str = "Medium") -> dict:
    counts = {"Short": 3, "Medium": 6, "Long": 10}
    n = counts.get(length, 6)
    summary = extractive_summary(text, num_sentences=n)
    points = key_points(text, num_points=5)

    return {
        "summary": summary,
        "key_points": points,
        "mode": "Extractive (Offline)",
        "original_words": word_count(text),
        "summary_words": word_count(summary),
    }

def summarize(text: str, length: str = "Medium") -> dict:
    if not is_ai_mode_available():
        return summarize_offline(text, length)

    base_endpoint = _clean_base_url(os.environ["AZURE_OPENAI_ENDPOINT"])
    api_key = os.environ["AZURE_OPENAI_API_KEY"].strip()
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"].strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()

    length_instruction = {
        "Short": "2-3 crisp sentences",
        "Medium": "1-2 comprehensive paragraphs",
        "Long": "3-4 detailed structured paragraphs",
    }.get(length, "1-2 paragraphs")

    prompt = f"""
You are an expert document summarizer. Summarize the following document clearly.
Length Requirement: {length_instruction}

Output format strictly:
SUMMARY:
<executive summary text>

KEY POINTS:
- Point 1
- Point 2
- Point 3
- Point 4
- Point 5

DOCUMENT:
{text[:50000]}
""".strip()

    try:
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=base_endpoint,
            api_key=api_key,
        )
        res = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4096,
        )
        raw = res.choices[0].message.content or ""

        summary_text = raw
        points = []
        if "KEY POINTS:" in raw:
            before, after = raw.split("KEY POINTS:", 1)
            summary_text = before.replace("SUMMARY:", "").strip()
            points = [
                line.lstrip("-•* ").strip()
                for line in after.splitlines()
                if line.strip() and line.strip().startswith(("-", "•", "*"))
            ]

        return {
            "summary": summary_text,
            "key_points": points[:5],
            "mode": f"Azure OpenAI ({deployment})",
            "original_words": word_count(text),
            "summary_words": word_count(summary_text),
        }
    except Exception as exc:
        print(f"[Summarizer AI Error]: {exc}")
        return summarize_offline(text, length)