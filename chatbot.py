"""
Ultra-fast ChatGPT-grade conversational engine with instant token streaming.
"""

import os
import re
from openai import AzureOpenAI

def _clean_base_url(url: str) -> str:
    match = re.match(r"^(https?://[^/]+)", url.strip())
    return match.group(1) if match else url.strip().rstrip("/")

def is_ai_mode_available() -> bool:
    return bool(
        os.getenv("AZURE_OPENAI_API_KEY")
        and os.getenv("AZURE_OPENAI_ENDPOINT")
        and os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )

# Reused client for low-latency TCP connection reuse
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

FAQ_KNOWLEDGE_BASE = [
    {"topic": "Admissions", "keywords": ["admission", "enrollment", "application"]},
    {"topic": "Exams & Grades", "keywords": ["exam", "gpa", "results", "revaluation"]},
    {"topic": "Fees & Aid", "keywords": ["fee", "tuition", "scholarship", "financial aid"]},
    {"topic": "Library", "keywords": ["library", "borrow", "e-book", "journal"]},
    {"topic": "Wellbeing", "keywords": ["stress", "anxiety", "counseling", "mental health"]},
]

def stream_answer(question: str, history: list):
    """
    Streams tokens in real-time (like ChatGPT) with sub-second Time To First Token.
    """
    if not is_ai_mode_available():
        yield "⚠️ Azure API credentials missing in `.env`. Please configure your key and endpoint."
        return

    client = get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4").strip()

    system_prompt = """
You are a brilliant, unrestricted, and highly versatile AI assistant (like ChatGPT / Claude).

Guidelines:
1. Answer ANY question across coding, computer science, mathematics, literature, general knowledge, problem solving, analysis, and creative writing.
2. For coding questions: Provide clean, idiomatic, fully working code with concise explanation and Markdown syntax highlighting.
3. Be direct, clear, intelligent, and engaging. Avoid unnecessary fluff.
4. Adapt naturally: If the user asks general questions, answer with full intelligence. If they ask about campus policies, provide helpful general college guidance.
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    # Keep last 8 turns for low latency & memory efficiency
    for msg in history[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    try:
        response_stream = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=4096,
            stream=True,
        )
        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
    except Exception as exc:
        yield f"⚠️ **Azure API Error:** `{exc}`"

def get_answer(question: str, history: list) -> str:
    """Non-streaming fallback."""
    full_text = ""
    for token in stream_answer(question, history):
        full_text += token
    return full_text