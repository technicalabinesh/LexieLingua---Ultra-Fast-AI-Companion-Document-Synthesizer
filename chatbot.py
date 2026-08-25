"""
LexieLingua - Optimized conversational engine with direct HTTP connection pooling and instant token streaming.
"""

import os
import re
import httpx
from openai import AzureOpenAI

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
    """Initializes and returns a pooled, low-latency AzureOpenAI client instance."""
    global _CLIENT
    if _CLIENT is None and is_ai_mode_available():
        base_endpoint = _clean_base_url(os.environ["AZURE_OPENAI_ENDPOINT"])
        api_key = os.environ["AZURE_OPENAI_API_KEY"].strip()
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview").strip()
        
        # Dedicated HTTP connection pooling for sub-100ms connection reuse
        http_client = httpx.Client(
            timeout=httpx.Timeout(connect=5.0, read=20.0, write=5.0, pool=30.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        )
        
        _CLIENT = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=base_endpoint,
            api_key=api_key,
            http_client=http_client,
        )
    return _CLIENT

FAQ_KNOWLEDGE_BASE = [
    {
        "topic": "Admissions",
        "keywords": ["admission", "enrollment", "apply", "application", "deadline", "eligibility"],
        "answer": "Admissions typically run on a semester basis. You can submit transcripts, standardized scores, and statements of purpose through the student portal."
    },
    {
        "topic": "Exams & Grading",
        "keywords": ["exam", "gpa", "results", "revaluation", "grade", "score", "credits"],
        "answer": "Grading follows a standard 4.0 scale or percentage grading. Final assessments and grade appeals must be submitted within 14 days of publication."
    },
    {
        "topic": "Fees & Scholarships",
        "keywords": ["fee", "tuition", "scholarship", "financial aid", "grant", "payment"],
        "answer": "Tuition installments can be paid online. Merit and need-based financial aid applications open prior to each academic term."
    },
]

def _offline_faq_answer(question: str) -> str:
    q_lower = question.lower()
    for entry in FAQ_KNOWLEDGE_BASE:
        if any(kw in q_lower for kw in entry["keywords"]):
            return f"**[Offline Knowledge Base - {entry['topic']}]**\n\n{entry['answer']}"
    return "⚡ **Offline Mode Active:** Configure Azure OpenAI credentials in `.env` for AI capabilities."

def stream_answer(question: str, history: list):
    """Streams tokens directly with minimized context overhead for maximum speed."""
    if not is_ai_mode_available():
        yield _offline_faq_answer(question)
        return

    client = get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip()

    system_prompt = (
        "You are LexieLingua, a fast and helpful assistant. Provide direct, accurate, and concise answers."
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    # Keep only the last 4 turns (fast TTFT + minimal token transfer)
    for msg in history[-4:]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
    messages.append({"role": "user", "content": question})

    try:
        response_stream = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=2048,
            stream=True,
        )

        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as exc:
        yield f"⚠️ **Azure API Error:** `{exc}`"
