"""
LexieLingua - Document Summarizer module with AI synthesis and offline fallback.
"""

import os
import re
from openai import AzureOpenAI
from utils import extractive_summary, key_points, word_count

def _clean_base_url(url: str) -> str:
    """Normalizes the Azure endpoint by stripping trailing paths."""
    if not url:
        return ""
    match = re.match(r"^(https?://[^/]+)", url.strip())
    return match.group(1) if match else url.strip().rstrip("/")

def is_ai_mode_available() -> bool:
    """Checks if required Azure OpenAI configuration is set in environment."""
    return bool(
        os.getenv("AZURE_OPENAI_API_KEY")
        and os.getenv("AZURE_OPENAI_ENDPOINT")
        and os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )

# Reused client instance for low-latency requests
_CLIENT = None

def get_client():
    """Initializes and returns a reusable AzureOpenAI client instance."""
    global _CLIENT
    if _CLIENT is None and is_ai_mode_available():
        base_endpoint = _clean_base_url(os.environ["AZURE_OPENAI_ENDPOINT"])
        api_key = os.environ["AZURE_OPENAI_API_KEY"].strip()
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()
        _CLIENT = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=base_endpoint,
            api_key=api_key,
        )
    return _CLIENT

def summarize_offline(text: str, length: str = "Medium") -> dict:
    """Deterministic local extraction fallback when cloud AI is unavailable."""
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
    """Generates structured summaries and bullet points using Azure OpenAI or local fallback."""
    if not text or not text.strip():
        return {
            "summary": "No readable text provided.",
            "key_points": [],
            "mode": "None",
            "original_words": 0,
            "summary_words": 0,
        }

    if not is_ai_mode_available():
        return summarize_offline(text, length)

    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4").strip()

    length_instruction = {
        "Short": "2-3 crisp, high-impact sentences",
        "Medium": "1-2 comprehensive and structured paragraphs",
        "Long": "3-4 detailed, high-density paragraphs with technical nuance",
    }.get(length, "1-2 comprehensive paragraphs")

    prompt = f"""
You are an expert document summarizer. Synthesize the provided document clearly and concisely.
Target Summary Length: {length_instruction}

Respond STRICTLY using this format:
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
        client = get_client()
        messages = [{"role": "user", "content": prompt}]

        # Parameter resilience across diverse model deployments
        try:
            res = client.chat.completions.create(
                model=deployment,
                messages=messages,
                max_completion_tokens=4096,
            )
        except Exception:
            res = client.chat.completions.create(
                model=deployment,
                messages=messages,
                max_tokens=4096,
            )

        raw = res.choices[0].message.content or ""

        # Resilient regex parser for SUMMARY and KEY POINTS
        summary_text = raw
        points = []

        kp_match = re.search(r"(?i)\*{0,2}KEY (?:POINTS|TAKEAWAYS)\*{0,2}:?", raw)
        if kp_match:
            split_pos = kp_match.start()
            summary_part = raw[:split_pos]
            points_part = raw[kp_match.end():]

            # Strip SUMMARY header if present
            summary_text = re.sub(r"(?i)^\s*\*{0,2}SUMMARY\*{0,2}:?\s*", "", summary_part).strip()

            # Parse lines starting with bullet indicators
            for line in points_part.splitlines():
                cleaned = line.strip()
                if cleaned and re.match(r"^[-•*–\d+\.]\s*", cleaned):
                    clean_pt = re.sub(r"^[-•*–\d+\.]\s*", "", cleaned).strip()
                    if clean_pt:
                        points.append(clean_pt)

        # Fallback if parser didn't find bullet markers
        if not points and summary_text:
            points = key_points(text, num_points=5)

        return {
            "summary": summary_text.strip(),
            "key_points": points[:5],
            "mode": f"Azure AI ({deployment})",
            "original_words": word_count(text),
            "summary_words": word_count(summary_text),
        }

    except Exception as exc:
        print(f"[Summarizer AI Error]: {exc}")
        return summarize_offline(text, length)
