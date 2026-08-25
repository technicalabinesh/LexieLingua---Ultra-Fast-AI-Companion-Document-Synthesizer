"""
LexieLingua - Ultra-fast ChatGPT-grade conversational engine with instant token streaming.
"""

import os
import re
from openai import AzureOpenAI

def _clean_base_url(url: str) -> str:
    """Strips paths and query parameters to ensure clean base endpoint."""
    if not url:
        return ""
    match = re.match(r"^(https?://[^/]+)", url.strip())
    return match.group(1) if match else url.strip().rstrip("/")

def is_ai_mode_available() -> bool:
    """Checks if valid Azure OpenAI configuration is set in environment."""
    return bool(
        os.getenv("AZURE_OPENAI_API_KEY")
        and os.getenv("AZURE_OPENAI_ENDPOINT")
        and os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )

# Singleton client for persistent connection pooling
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

# Knowledge base for offline mode
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
    {
        "topic": "Library & Research",
        "keywords": ["library", "borrow", "e-book", "journal", "research", "database"],
        "answer": "The digital library portal offers 24/7 access to IEEE, JSTOR, ScienceDirect, and catalog checkouts with your student ID."
    },
    {
        "topic": "Student Support",
        "keywords": ["stress", "anxiety", "counseling", "mental health", "support", "advisor"],
        "answer": "Academic advisors and confidential counseling services are accessible through the student wellness center and online booking."
    },
]

def _offline_faq_answer(question: str) -> str:
    """Matches user questions against local knowledge base when offline."""
    q_lower = question.lower()
    for entry in FAQ_KNOWLEDGE_BASE:
        if any(kw in q_lower for kw in entry["keywords"]):
            return f"**[Offline Knowledge Base - {entry['topic']}]**\n\n{entry['answer']}"
    
    return (
        "⚡ **Offline Mode Active:** Azure OpenAI credentials are not configured in `.env`.\n\n"
        "You can configure `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_OPENAI_DEPLOYMENT` "
        "to unlock full reasoning, coding synthesis, and mathematical problem-solving."
    )

def stream_answer(question: str, history: list):
    """
    Streams tokens in real-time with sub-second Time To First Token (TTFT).
    """
    if not is_ai_mode_available():
        yield _offline_faq_answer(question)
        return

    client = get_client()
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4").strip()

    system_prompt = (
        "You are LexieLingua Copilot, a brilliant, unrestricted, and highly capable AI assistant.\n\n"
        "Guidelines:\n"
        "1. Answer ANY question across coding, CS, mathematics, essays, analysis, and problem-solving.\n"
        "2. For coding: Provide clean, fully working code with clear markdown syntax highlighting and comments.\n"
        "3. Provide structured, accurate, and direct responses without unnecessary filler."
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    # Maintain sliding context window (last 8 turns) for speed and token economy
    for msg in history[-8:]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
    messages.append({"role": "user", "content": question})

    try:
        # Try modern parameter (max_completion_tokens) first
        try:
            response_stream = client.chat.completions.create(
                model=deployment,
                messages=messages,
                max_completion_tokens=4096,
                stream=True,
            )
        except Exception:
            # Fallback to standard max_tokens for older model versions
            response_stream = client.chat.completions.create(
                model=deployment,
                messages=messages,
                max_tokens=4096,
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
    """Non-streaming synchronous fallback."""
    full_text = ""
    for token in stream_answer(question, history):
        full_text += token
    return full_text
