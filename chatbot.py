"""
LexieLingua - Ultra-fast conversational engine with instant token streaming.
"""

import os
import re
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
    return "⚡ **Offline Mode Active:** Azure OpenAI credentials are not configured in `.env`."

def stream_answer(question: str, history: list):
    """Streams tokens in real-time with resilient parameter handling."""
    if not is_ai_mode_available():
        yield _offline_faq_answer(question)
        return

    client = get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip()

    system_prompt = (
        "You are LexieLingua Copilot, a fast, accurate AI assistant. "
        "Provide direct, clear, structured responses with working code examples when applicable."
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in history[-4:]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
    messages.append({"role": "user", "content": question})

    response_stream = None
    try:
        # First attempt: modern max_completion_tokens parameter
        response_stream = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=2048,
            stream=True,
        )
    except Exception as e1:
        if "max_completion_tokens" in str(e1) or "unsupported_parameter" in str(e1).lower():
            try:
                # Fallback for older model versions
                response_stream = client.chat.completions.create(
                    model=deployment,
                    messages=messages,
                    max_tokens=2048,
                    stream=True,
                )
            except Exception as e2:
                yield f"⚠️ **Azure API Error:** `{e2}`"
                return
        else:
            yield f"⚠️ **Azure API Error:** `{e1}`"
            return

    try:
        for chunk in response_stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
    except Exception as exc:
        yield f"⚠️ **Stream Interruption:** `{exc}`"

def get_answer(question: str, history: list) -> str:
    full_text = ""
    for token in stream_answer(question, history):
        full_text += token
    return full_text
