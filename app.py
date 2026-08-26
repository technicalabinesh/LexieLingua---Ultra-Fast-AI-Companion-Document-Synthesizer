"""
LexieLingua AI - Next-Gen Student Copilot & Document Intelligence Platform
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
# ASYNC HISTORY LOGGERS
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
# PIXSO-INSPIRED ULTRA-MODERN CSS
# ============================================================
PIXSO_SAAS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary-pink: #FF1361;
    --primary-purple: #903AFF;
    --primary-gradient: linear-gradient(135deg, #FF1361 0%, #903AFF 100%);
    --card-bg: rgba(255, 255, 255, 0.88);
    --card-border: rgba(255, 255, 255, 0.95);
    --glow-shadow: 0 20px 45px -15px rgba(255, 19, 97, 0.18), 0 10px 30px -10px rgba(144, 58, 255, 0.15);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

/* Pixso Sunset Mesh Gradient Canvas */
.stApp {
    background: 
        radial-gradient(circle at 12% 18%, rgba(255, 46, 147, 0.38) 0%, transparent 45%),
        radial-gradient(circle at 88% 12%, rgba(144, 58, 255, 0.35) 0%, transparent 50%),
        radial-gradient(circle at 50% 88%, rgba(251, 146, 60, 0.28) 0%, transparent 45%),
        linear-gradient(145deg, #FDF2F8 0%, #F5F3FF 40%, #FFF7ED 100%) !important;
    background-attachment: fixed;
}

.main .block-container {
    max-width: 1260px;
    padding: 1.2rem 2rem 4rem;
}

/* Header Frosted Navbar */
.nav-container {
    background: rgba(255, 255, 255, 0.82) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-radius: 9999px;
    padding: 12px 28px;
    box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.05);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-logo {
    font-size: 1.35rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #FF1361 0%, #903AFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    gap: 8px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    background: #F0FDF4 !important;
    color: #166534 !important;
    border: 1px solid #BBF7D0;
}

.status-dot {
    width: 8px;
    height: 8px;
    background-color: #22C55E;
    border-radius: 50%;
    box-shadow: 0 0 10px #22C55E;
}

/* Hero Section */
.hero-wrapper {
    padding: 8px 0 20px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 800;
    color: #FF1361;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(255, 19, 97, 0.2);
    box-shadow: 0 4px 12px rgba(255, 19, 97, 0.08);
    margin-bottom: 12px;
}

.hero-main-title {
    font-size: 2.8rem;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -0.04em;
    color: #0F172A;
    margin-bottom: 10px;
}

.hero-gradient-text {
    background: linear-gradient(135deg, #FF1361 0%, #7928CA 60%, #4F46E5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-desc {
    font-size: 1.02rem;
    color: #475569;
    line-height: 1.6;
    max-width: 720px;
    margin-bottom: 16px;
}

/* Floating Glassmorphic App Window */
.mockup-window {
    background: var(--card-bg) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1.5px solid var(--card-border) !important;
    border-radius: 28px !important;
    box-shadow: var(--glow-shadow), 0 25px 50px -12px rgba(0, 0, 0, 0.06) !important;
    padding: 24px 28px;
    margin-bottom: 18px;
}

.window-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(226, 232, 240, 0.8);
    padding-bottom: 12px;
    margin-bottom: 16px;
}

.window-dots {
    display: flex;
    gap: 6px;
}
.dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.dot-red { background: #FF5F56; }
.dot-yellow { background: #FFBD2E; }
.dot-green { background: #27C93F; }

.ui-card {
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.95) !important;
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.05);
    margin-bottom: 16px;
}

/* Nav & Action Buttons */
div[data-testid="stButton"] > button {
    border-radius: 9999px !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    min-height: 44px !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #1E293B !important;
    border: 1.5px solid #E2E8F0 !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #FFFFFF !important;
    border-color: #FF1361 !important;
    color: #FF1361 !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(255, 19, 97, 0.12) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.18) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.25) !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 9999px !important;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08) !important;
    padding: 4px 8px !important;
}

.chat-user {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
    color: #FFFFFF !important;
    padding: 14px 22px;
    border-radius: 24px 24px 4px 24px;
    margin: 12px 0 12px auto;
    max-width: 82%;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15);
    font-size: 0.96rem;
    line-height: 1.55;
}
.chat-user * { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }

.chat-ai {
    background: #FFFFFF !important;
    color: #0F172A !important;
    padding: 18px 24px;
    border-radius: 24px 24px 24px 4px;
    margin: 12px 0;
    max-width: 90%;
    border: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04);
    font-size: 0.96rem;
    line-height: 1.65;
}

/* Beautiful Frosted File Uploader (No Dark Box) */
div[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.95) !important;
    border-radius: 24px !important;
    padding: 16px !important;
    box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.04) !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #FAFAFC !important;
    border: 2px dashed #CBD5E1 !important;
    border-radius: 18px !important;
    padding: 24px 16px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: #334155 !important;
}

.metric-box {
    background: rgba(255, 255, 255, 0.92) !important;
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-radius: 22px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04);
}
.metric-val {
    font-size: 1.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #FF1361 0%, #7928CA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-lbl {
    font-size: 0.74rem;
    color: #64748B !important;
    font-weight: 800;
    text-transform: uppercase;
    margin-top: 2px;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(PIXSO_SAAS_CSS, unsafe_allow_html=True)

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
    '<span class="status-pill"><span class="status-dot"></span>Low-Latency Engine Active</span>'
    if ai_connected
    else '<span class="status-pill" style="background:#FFFBEB; color:#B45309; border-color:#FDE68A;">● Offline Mode</span>'
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
    # Pixso Landing Hero
    st.markdown(
        '<div class="hero-wrapper">'
        '<div class="hero-badge">⚡ Next-Gen Student Copilot</div>'
        '<div class="hero-main-title">AI Intelligence for <span class="hero-gradient-text">Brighter Minds</span></div>'
        '<div class="hero-desc">Unleash your learning with LexieLingua AI. Ask any programming, mathematical, or academic inquiry with sub-second streaming answers and real-time document analysis.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([2.6, 1.1])

    with left_col:
        # Floating macOS Window Mockup
        st.markdown(
            '<div class="mockup-window">'
            '<div class="window-header">'
            '<div class="window-dots"><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></div>'
            '<div style="font-size:0.8rem; font-weight:800; color:#64748B;">copilot.lexielingua.ai</div>'
            '<div style="width:40px;"></div>'
            '</div>',
            unsafe_allow_html=True,
        )

        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(
                    '<div class="chat-ai">👋 <b>Welcome! I am LexieLingua AI.</b><br>Ask me any coding algorithm, math derivation, or exam question to get an instant answer.</div>',
                    unsafe_allow_html=True,
                )

            for turn in st.session_state.chat_history:
                if turn["role"] == "user":
                    st.markdown(
                        f'<div class="chat-user">'
                        f'<div style="font-size:0.75rem; opacity:0.8; margin-bottom:4px; font-weight:700;">👤 You</div>'
                        f'<div>{turn["content"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    with st.container():
                        st.markdown(
                            '<div style="font-size:0.78rem; color:#FF1361; font-weight:800; margin:8px 0 2px;">✨ LexieLingua AI</div>',
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
                f'<div style="font-size:0.75rem; opacity:0.8; margin-bottom:4px; font-weight:700;">👤 You</div>'
                f'<div>{user_input}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            save_chat_message(st.session_state.session_id, "user", user_input)

            st.markdown('<div style="font-size:0.78rem; color:#FF1361; margin:12px 0 4px; font-weight:800;">✨ LexieLingua AI</div>', unsafe_allow_html=True)
            stream_gen = stream_answer(user_input, st.session_state.chat_history)
            full_ai_response = st.write_stream(stream_gen)

            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": full_ai_response})
            save_chat_message(st.session_state.session_id, "assistant", full_ai_response)

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.chat_history:
            if st.button("🗑 Clear Chat History", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()

    with right_col:
        st.markdown(
            '<div class="ui-card">'
            '<div style="font-size:0.78rem; font-weight:800; color:#FF1361; text-transform:uppercase; margin-bottom:4px;">Quick Actions</div>'
            '<h4 style="margin:0 0 12px; font-weight:900; font-size:1.05rem;">⚡ Instant Prompts</h4>',
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
        '<div class="hero-wrapper">'
        '<div class="hero-badge">📄 AI Document Intelligence</div>'
        '<div class="hero-main-title">Synthesize Knowledge <span class="hero-gradient-text">Instantly</span></div>'
        '<div class="hero-desc">Drop your research papers, lecture notes, or textbooks (PDF, DOCX, TXT) to get actionable takeaways and structured summaries in seconds.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    up_col, opt_col = st.columns([2.2, 1])
    with up_col:
        doc_file = st.file_uploader("Upload document", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
    with opt_col:
        summary_len = st.select_slider("Detail Level", options=["Short", "Medium", "Long"], value="Medium")
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
                    f'<div style="font-size:0.78rem; font-weight:800; color:#FF1361; text-transform:uppercase; margin-bottom:6px;">Synthesized Overview</div>'
                    f'<h3 style="margin:0 0 12px; font-weight:900; font-size:1.15rem;">📝 Executive Summary</h3>',
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

                doc_record = {
                    "filename": doc_file.name,
                    "file_type": doc_file.name.split(".")[-1].upper(),
                    "summary": full_summary,
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "original_words": len(raw_text.split()),
                    "summary_words": len(full_summary.split()),
                }
                st.session_state.local_doc_history.insert(0, doc_record)

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
        '<div class="hero-wrapper">'
        '<div class="hero-badge">📊 Audit & Records</div>'
        '<div class="hero-main-title">Activity & <span class="hero-gradient-text">History Logs</span></div>'
        '<div class="hero-desc">Review your past conversations, questions asked, uploaded files, and generated document summaries.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    h_col1, h_col2 = st.columns(2)

    with h_col1:
        st.markdown(
            '<div class="ui-card">'
            '<h3 style="margin:0 0 12px; font-weight:900; font-size:1.1rem;">💬 Questions & Chat History</h3>',
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
            '<h3 style="margin:0 0 12px; font-weight:900; font-size:1.1rem;">📁 Uploaded Documents & Summaries</h3>',
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
        '<div class="hero-wrapper">'
        '<div class="hero-badge">⚡ Architecture Specs</div>'
        '<div class="hero-main-title">High-Throughput <span class="hero-gradient-text">Neural Foundry</span></div>'
        '<div class="hero-desc">Built with persistent HTTP connection pooling and non-blocking asynchronous threads for instantaneous sub-150ms token generation.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-box"><div class="metric-val">&lt; 150 ms</div><div class="metric-lbl">Time to First Token</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-box"><div class="metric-val">Async</div><div class="metric-lbl">Non-Blocking I/O</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-box"><div class="metric-val">Pooled</div><div class="metric-lbl">Persistent Connection</div></div>', unsafe_allow_html=True)
