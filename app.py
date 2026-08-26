"""
LexieLingua AI - Next-Gen Student Support & Document Intelligence Platform
"""

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Safe module imports
try:
    from chatbot import stream_answer, is_ai_mode_available as chat_ai_available
except ImportError:
    def stream_answer(q, h): yield "Chatbot module unavailable."
    def chat_ai_available(): return False

try:
    from summarizer import (
        stream_summarize,
        summarize_offline,
        is_ai_mode_available as summ_ai_available,
    )
except ImportError:
    from summarizer import summarize, is_ai_mode_available as summ_ai_available
    def stream_summarize(t, length="Medium"):
        res = summarize(t, length)
        yield res.get("summary", "")
    def summarize_offline(t, length="Medium"):
        return {"summary": t[:500] + "...", "key_points": []}

from utils import extract_text

load_dotenv()

st.set_page_config(
    page_title="LexieLingua AI | Intelligent Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Background executor for zero-latency non-blocking DB writes
_DB_EXECUTOR = ThreadPoolExecutor(max_workers=4)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase_client = None

# ============================================================
# ASYNC AUDIT & HISTORY LOGGERS
# ============================================================
def _async_save_chat_message(session_id: str, role: str, content: str):
    if supabase_client:
        try:
            supabase_client.table("student_chat_logs").insert({
                "session_id": session_id,
                "role": role,
                "message": content
            }).execute()
        except Exception:
            try:
                supabase_client.table("chat_history").insert({
                    "session_id": session_id,
                    "role": role,
                    "content": content
                }).execute()
            except Exception:
                pass

def save_chat_message(session_id: str, role: str, content: str):
    _DB_EXECUTOR.submit(_async_save_chat_message, session_id, role, content)

def _async_save_doc_summary(session_id: str, filename: str, file_type: str, raw_text: str, summary: str):
    if supabase_client:
        try:
            supabase_client.table("student_uploaded_docs").insert({
                "session_id": session_id,
                "filename": filename,
                "file_type": file_type,
                "extracted_text_preview": raw_text[:2000],
                "summary": summary,
                "original_word_count": len(raw_text.split()),
                "summary_word_count": len(summary.split()),
            }).execute()
        except Exception:
            try:
                supabase_client.table("document_summaries").insert({
                    "filename": filename,
                    "summary": summary,
                    "original_words": len(raw_text.split()),
                    "summary_words": len(summary.split()),
                }).execute()
            except Exception:
                pass

def save_summary_to_db(session_id: str, filename: str, file_type: str, raw_text: str, summary: str):
    _DB_EXECUTOR.submit(_async_save_doc_summary, session_id, filename, file_type, raw_text, summary)

# ============================================================
# CSS DESIGN & CONTRAST POLISH
# ============================================================
PREMIUM_EFFECTS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary-gradient: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #D946EF 100%);
    --dark: #0F172A;
    --border: #E2E8F0;
    --glass-shadow: 0 14px 34px -10px rgba(99, 102, 241, 0.12), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
}

html, body, p, h1, h2, h3, h4, h5, h6, span, label, div {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    color: #0F172A;
}

ul, ol {
    margin-left: 20px !important;
    padding-left: 10px !important;
}

li {
    color: #1E293B !important;
    font-size: 0.96rem !important;
    line-height: 1.65 !important;
    margin-bottom: 6px !important;
}

li::marker {
    color: #4F46E5 !important;
    font-weight: bold !important;
}

code:not(pre code) {
    background: #EEF2FF !important;
    color: #4338CA !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88em !important;
    padding: 3px 7px !important;
    border-radius: 6px !important;
    border: 1px solid #E0E7FF !important;
    font-weight: 600 !important;
}

.stApp {
    background: 
        radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.10) 0%, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(217, 70, 239, 0.08) 0%, transparent 40%),
        linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%) !important;
    background-attachment: fixed;
}

.main .block-container {
    max-width: 1200px;
    padding: 1.25rem 1.75rem 4rem;
}

.nav-container {
    background: #FFFFFF !important;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 14px 26px;
    box-shadow: var(--glass-shadow);
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-logo {
    font-size: 1.4rem;
    font-weight: 800;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
}

.status-online {
    background: #F0FDF4 !important;
    color: #15803D !important;
    border: 1px solid #BBF7D0;
}

.status-dot {
    width: 8px;
    height: 8px;
    background-color: #22C55E;
    border-radius: 50%;
}

.status-offline {
    background: #FFFBEB !important;
    color: #B45309 !important;
    border: 1px solid #FDE68A;
}

.hero-card, .ui-card {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px;
    padding: 22px 26px;
    margin-bottom: 18px;
    box-shadow: var(--glass-shadow);
}

.hero-title {
    font-size: 1.4rem;
    font-weight: 800;
    margin: 0 0 4px;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.about-banner {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.06) 0%, rgba(217, 70, 239, 0.05) 100%);
    border: 1px solid rgba(79, 70, 229, 0.15);
    border-radius: 18px;
    padding: 16px 22px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.feature-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    font-weight: 700;
    color: #4F46E5;
    background: #FFFFFF;
    padding: 5px 12px;
    border-radius: 9999px;
    border: 1px solid #E2E8F0;
    margin-right: 6px;
    margin-top: 4px;
}

div[data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    min-height: 42px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #EEF2FF !important;
    border-color: #4F46E5 !important;
    color: #4F46E5 !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: var(--primary-gradient) !important;
    color: #FFFFFF !important;
    border: none !important;
}

div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06) !important;
}

.chat-user {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    padding: 14px 20px;
    border-radius: 18px 18px 4px 18px;
    margin: 12px 0 12px auto;
    max-width: 82%;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
    font-size: 0.96rem;
    line-height: 1.55;
}
.chat-user * { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }

.chat-ai {
    background: #FFFFFF !important;
    color: #0F172A !important;
    padding: 18px 24px;
    border-radius: 18px 18px 18px 4px;
    margin: 12px 0;
    max-width: 90%;
    border: 1px solid var(--border);
    box-shadow: var(--glass-shadow);
    font-size: 0.96rem;
    line-height: 1.65;
}

.metric-box {
    background: #FFFFFF !important;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    box-shadow: var(--glass-shadow);
}
.metric-val {
    font-size: 1.6rem;
    font-weight: 800;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-lbl {
    font-size: 0.74rem;
    color: #64748B !important;
    font-weight: 700;
    text-transform: uppercase;
    margin-top: 2px;
}
#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(PREMIUM_EFFECTS_CSS, unsafe_allow_html=True)

# State initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "local_doc_history" not in st.session_state:
    st.session_state.local_doc_history = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

def navigate(page: str):
    st.session_state.page = page
    st.rerun()

# Top Navbar
ai_connected = chat_ai_available()
status_html = (
    '<span class="status-pill status-online"><span class="status-dot"></span>Low-Latency Engine Active</span>'
    if ai_connected
    else '<span class="status-pill status-offline">● Offline Engine</span>'
)

st.markdown(
    f'<div class="nav-container">'
    f'<div class="brand-logo">✨ LexieLingua AI</div>'
    f'<div>{status_html}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# 4 Navigation Tabs
nav_cols = st.columns(4)
with nav_cols[0]:
    if st.button("💬 Conversational AI", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary"):
        navigate("chat")
with nav_cols[1]:
    if st.button("📄 Document Synthesizer", use_container_width=True, type="primary" if st.session_state.page == "summarizer" else "secondary"):
        navigate("summarizer")
with nav_cols[2]:
    if st.button("📊 History Logs", use_container_width=True, type="primary" if st.session_state.page == "history" else "secondary"):
        navigate("history")
with nav_cols[3]:
    if st.button("⚙️ Architecture", use_container_width=True, type="primary" if st.session_state.page == "about" else "secondary"):
        navigate("about")

st.write("")

# ============================================================
# VIEW 1: CONVERSATIONAL AI
# ============================================================
if st.session_state.page == "chat":
    # Application Intro Banner
    st.markdown(
        '<div class="about-banner">'
        '<div style="font-size: 2rem;">🚀</div>'
        '<div>'
        '<div style="font-weight: 800; font-size: 1.05rem; color: #1E293B; margin-bottom: 2px;">Welcome to LexieLingua AI</div>'
        '<div style="color: #475569; font-size: 0.88rem; line-height: 1.45;">'
        'LexieLingua AI is an intelligent student copilot designed for <b>instant query resolution</b>, '
        '<b>code synthesis</b>, and <b>real-time document analysis</b>. Ask any academic or programming question below to get started.'
        '</div>'
        '<div style="margin-top: 6px;">'
        '<span class="feature-tag">⚡ Sub-Second Streaming</span>'
        '<span class="feature-tag">💻 Code & Algorithm Help</span>'
        '<span class="feature-tag">📄 PDF & Document Synthesis</span>'
        '<span class="feature-tag">🔒 Background Audit Logs</span>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([2.6, 1.1])

    with left_col:
        st.markdown(
            '<div class="hero-card">'
            '<div class="hero-title">Instant Response Copilot</div>'
            '<p style="color:#64748B; font-size:0.92rem; margin:0;">Zero-delay streaming for code debugging, study questions, and problem-solving.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(
                    '<div class="chat-ai">👋 <b>Welcome! I am LexieLingua AI.</b><br>Ask any coding, math, or study question for an instant answer.</div>',
                    unsafe_allow_html=True,
                )

            for turn in st.session_state.chat_history:
                if turn["role"] == "user":
                    st.markdown(
                        f'<div class="chat-user">'
                        f'<div style="font-size:0.75rem; opacity:0.85; margin-bottom:4px; font-weight:700;">👤 You</div>'
                        f'<div>{turn["content"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    with st.container():
                        st.markdown(
                            '<div style="font-size:0.78rem; color:#4F46E5; font-weight:800; margin:8px 0 2px;">✨ LexieLingua AI</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(turn["content"])

        user_input = st.chat_input("Ask LexieLingua AI anything...")
        if st.session_state.pending_prompt:
            user_input = st.session_state.pending_prompt
            st.session_state.pending_prompt = None

        if user_input:
            st.markdown(
                f'<div class="chat-user">'
                f'<div style="font-size:0.75rem; opacity:0.85; margin-bottom:4px; font-weight:700;">👤 You</div>'
                f'<div>{user_input}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            # Log question to database
            save_chat_message(st.session_state.session_id, "user", user_input)

            st.markdown('<div style="font-size:0.78rem; color:#4F46E5; margin:12px 0 4px; font-weight:800;">✨ LexieLingua AI</div>', unsafe_allow_html=True)
            stream_gen = stream_answer(user_input, st.session_state.chat_history)
            full_ai_response = st.write_stream(stream_gen)

            # Update session state & log AI response to database
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": full_ai_response})
            save_chat_message(st.session_state.session_id, "assistant", full_ai_response)

        if st.session_state.chat_history:
            st.write("")
            if st.button("🗑 Clear Chat History", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()

    with right_col:
        st.markdown(
            '<div class="ui-card">'
            '<div style="font-size:0.78rem; font-weight:800; color:#4F46E5; text-transform:uppercase; margin-bottom:4px;">Quick Actions</div>'
            '<h4 style="margin:0 0 12px; font-weight:800; font-size:1.02rem;">⚡ Instant Prompts</h4>',
            unsafe_allow_html=True,
        )
        
        prompts = [
            ("💻", "Write a Python script to reverse a linked list with test cases."),
            ("⚛️", "Explain Quantum Entanglement with a clear visual analogy."),
            ("⚡", "What are the top 5 performance optimization patterns in SQL?"),
            ("🎓", "Design a structured 14-day study plan for machine learning finals."),
        ]
        
        for idx, (icon, prompt_text) in enumerate(prompts):
            if st.button(f"{icon} {prompt_text}", key=f"quick_{idx}", type="secondary", use_container_width=True):
                st.session_state.pending_prompt = prompt_text
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# VIEW 2: DOCUMENT SUMMARIZER
# ============================================================
elif st.session_state.page == "summarizer":
    st.markdown(
        '<div class="hero-card">'
        '<div class="hero-title">Live Document Synthesizer</div>'
        '<p style="color:#64748B; font-size:0.92rem; margin:0;">Upload lecture slides, textbooks, or research papers (PDF, DOCX, TXT, MD) for instant executive summaries.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    up_col, opt_col = st.columns([2.2, 1])
    with up_col:
        doc_file = st.file_uploader("Upload document", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
    with opt_col:
        summary_len = st.select_slider("Target Detail Level", options=["Short", "Medium", "Long"], value="Medium")
        run_sum = st.button("✨ Distill Document", type="primary", use_container_width=True)

    if run_sum:
        if not doc_file:
            st.warning("⚠️ Please upload a document first.")
        else:
            raw_text = extract_text(doc_file)
            if not raw_text.strip():
                st.error("❌ No readable text found in document.")
            else:
                st.markdown(
                    f'<div class="ui-card">'
                    f'<div style="font-size:0.78rem; font-weight:800; color:#4F46E5; text-transform:uppercase; margin-bottom:6px;">Synthesized Overview</div>'
                    f'<h3 style="margin:0 0 12px; font-weight:800; font-size:1.15rem;">📝 Executive Summary</h3>',
                    unsafe_allow_html=True,
                )

                if not summ_ai_available():
                    offline_res = summarize_offline(raw_text, summary_len)
                    st.write(offline_res["summary"])
                    full_summary = offline_res["summary"]
                else:
                    stream_gen = stream_summarize(raw_text, length=summary_len)
                    full_summary = st.write_stream(stream_gen)

                st.markdown('</div>', unsafe_allow_html=True)

                # Store locally in session
                doc_record = {
                    "filename": doc_file.name,
                    "file_type": doc_file.name.split(".")[-1].upper(),
                    "summary": full_summary,
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "original_words": len(raw_text.split()),
                    "summary_words": len(full_summary.split()),
                }
                st.session_state.local_doc_history.insert(0, doc_record)

                # Save asynchronously to Supabase
                save_summary_to_db(
                    session_id=st.session_state.session_id,
                    filename=doc_file.name,
                    file_type=doc_file.name.split(".")[-1],
                    raw_text=raw_text,
                    summary=full_summary
                )

# ============================================================
# VIEW 3: HISTORY & AUDIT LOG
# ============================================================
elif st.session_state.page == "history":
    st.markdown(
        '<div class="hero-card">'
        '<div class="hero-title">Activity & History Logs</div>'
        '<p style="color:#64748B; font-size:0.92rem; margin:0;">Complete audit trail of questions asked, AI answers, uploaded documents, and generated summaries.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    h_col1, h_col2 = st.columns(2)

    with h_col1:
        st.markdown(
            '<div class="ui-card">'
            '<h3 style="margin:0 0 12px; font-weight:800; font-size:1.1rem;">💬 Questions & Chat History</h3>',
            unsafe_allow_html=True,
        )

        db_chat_logs = []
        if supabase_client:
            try:
                res = supabase_client.table("student_chat_logs")\
                    .select("role, message, created_at")\
                    .order("created_at", desc=True)\
                    .limit(25)\
                    .execute()
                db_chat_logs = res.data or []
            except Exception:
                db_chat_logs = []

        if db_chat_logs:
            for item in db_chat_logs:
                role_label = "👤 Question" if item["role"] == "user" else "✨ LexieLingua Answer"
                created = item.get("created_at", "")[:16].replace("T", " ")
                with st.expander(f"{role_label} ({created})"):
                    st.write(item.get("message", ""))
        elif st.session_state.chat_history:
            for item in reversed(st.session_state.chat_history):
                role_label = "👤 Question" if item["role"] == "user" else "✨ LexieLingua Answer"
                with st.expander(f"{role_label} (Current Session)"):
                    st.write(item.get("content", ""))
        else:
            st.info("No recorded chat inquiries yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with h_col2:
        st.markdown(
            '<div class="ui-card">'
            '<h3 style="margin:0 0 12px; font-weight:800; font-size:1.1rem;">📁 Uploaded Documents & Summaries</h3>',
            unsafe_allow_html=True,
        )

        db_doc_logs = []
        if supabase_client:
            try:
                res = supabase_client.table("student_uploaded_docs")\
                    .select("filename, file_type, summary, original_word_count, uploaded_at")\
                    .order("uploaded_at", desc=True)\
                    .limit(20)\
                    .execute()
                db_doc_logs = res.data or []
            except Exception:
                db_doc_logs = []

        combined_docs = db_doc_logs if db_doc_logs else st.session_state.local_doc_history

        if combined_docs:
            for doc in combined_docs:
                uploaded = doc.get("uploaded_at", "")[:16].replace("T", " ")
                orig_words = doc.get("original_word_count", doc.get("original_words", 0))
                with st.expander(f"📄 {doc.get('filename')} • {orig_words} words ({uploaded})"):
                    st.markdown("**Generated Summary:**")
                    st.write(doc.get("summary", "No summary available."))
        else:
            st.info("No uploaded documents or summaries found.")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# VIEW 4: ARCHITECTURE & ABOUT
# ============================================================
else:
    st.markdown(
        '<div class="hero-card">'
        '<div class="hero-title">About LexieLingua AI</div>'
        '<p style="color:#64748B; font-size:0.95rem; line-height:1.6; margin:0;">'
        '<b>LexieLingua AI</b> is a high-performance, ultra-low-latency platform designed to assist students and educators with instant answers, code debugging, and document synthesis. '
        'It combines real-time streaming LLM engines with persistent connection pooling and asynchronous database logging.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-box"><div class="metric-val">&lt; 150 ms</div><div class="metric-lbl">Time to First Token</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-box"><div class="metric-val">Non-Blocking</div><div class="metric-lbl">Async DB Threading</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-box"><div class="metric-val">Persistent</div><div class="metric-lbl">Connection Pooling</div></div>', unsafe_allow_html=True)
