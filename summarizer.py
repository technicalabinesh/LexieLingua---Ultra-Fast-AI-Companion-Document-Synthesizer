"""
LexieLingua - Instant streaming document summarizer module.
"""

import os
import re
from openai import AzureOpenAI
from utils import extractive_summary, key_points, word_count

def _clean_base_url(url: str) -> str:
    if not url:
        return ""
    match = re.match(r"^(https?://[^/]+)", url.strip())
    return match.group(1) if match else url.strip().rstrip("/")

def is_ai_mode_available() -> bool:
    return bool(
        os.getenv("AZURE_OPENAI_API_KEY")
        and os.getenv("AZURE_OPENAI_ENDPOINT")
        and os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )

_CLIENT = None

def get_client():
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

def stream_summarize(text: str, length: str = "Medium"):
    """Streams summary tokens with parameter resilience."""
    if not is_ai_mode_available():
        offline_res = summarize_offline(text, length)
        yield offline_res["summary"]
        return

    client = get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip()

    length_instruction = {
        "Short": "2-3 concise sentences",
        "Medium": "1 structured paragraph",
        "Long": "2-3 comprehensive paragraphs",
    }.get(length, "1 structured paragraph")

    prompt = (
        f"Synthesize the following document into {length_instruction}.\n\n"
        f"DOCUMENT:\n{text[:15000]}"
    )

    response_stream = None
    try:
        response_stream = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1024,
            stream=True,
        )
    except Exception as e1:
        if "max_completion_tokens" in str(e1) or "unsupported_parameter" in str(e1).lower():
            try:
                response_stream = client.chat.completions.create(
                    model=deployment,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                    stream=True,
                )
            except Exception as e2:
                yield f"⚠️ Summary Error: {e2}"
                return
        else:
            yield f"⚠️ Summary Error: {e1}"
            return

    try:
        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
    except Exception as exc:
        yield f"⚠️ Summary Error: {exc}"

def summarize(text: str, length: str = "Medium") -> dict:
    full_text = ""
    for chunk in stream_summarize(text, length):
        full_text += chunk

    pts = key_points(text, num_points=5)
    return {
        "summary": full_text.strip(),
        "key_points": pts,
        "mode": f"Azure AI ({os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')})" if is_ai_mode_available() else "Extractive (Offline)",
        "original_words": word_count(text),
        "summary_words": word_count(full_text),
    }
