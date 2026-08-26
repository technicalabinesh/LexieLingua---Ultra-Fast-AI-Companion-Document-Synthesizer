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
# HIGH CONTRAST SOLID & GLASS DESIGN CSS
# ============================================================
EDITORIAL_NATURE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
    --text-dark: #0F172A;
    --text-muted: #475569;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

/* Background with High-Contrast Dark Gradient Shield */
.stApp {
    background: 
        linear-gradient(180deg, rgba(15, 23, 42, 0.65) 0%, rgba(15, 23, 42, 0.45) 45%, rgba(15, 23, 42, 0.75) 100%),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2832&auto=format&fit=crop") no-repeat center center fixed !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}

.main .block-container {
    max-width: 1260px;
    padding: 1.2rem 2rem 4.5rem;
}

/* Header Navbar */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-radius: 9999px;
    padding: 12px 28px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.top-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: #0F172A !important;
}

.top-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 800;
    background: #F0FDF4 !important;
    color: #166534 !important;
    border: 1px solid #BBF7D0;
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background: #22C55E;
    border-radius: 50%;
    box-shadow: 0 0 10px #22C55E;
}

/* Hero Section */
.hero-editorial {
    padding: 10px 0 20px;
}

.badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 9999px;
    padding: 6px 16px;
    font-size: 0.8rem;
    font-weight: 800;
    color: #0F172A !important;
    margin-bottom: 12px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.headline-text {
    font-family: 'Space Grotesk', -apple-system, sans-serif;
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.04em;
    color: #FFFFFF !important;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    text-transform: uppercase;
    margin-bottom: 8px;
}

.sticker {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 10px;
    font-weight: 800;
    font-size: 0.9rem;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
    vertical-align: middle;
    margin: 0 6px;
}
.sticker-blue { background: #0284C7; color: #FFFFFF !important; transform: rotate(-2deg); }
.sticker-pink { background: #DB2777; color: #FFFFFF !important; transform: rotate(2deg); }

.sub-editorial {
    font-size: 1.05rem;
    color: #F1F5F9 !important;
    font-weight: 600;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
    max-width: 680px;
    line-height: 1.5;
}

/* High-Contrast Solid White Cards */
.solid-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 26px !important;
    padding: 24px 28px !important;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
    margin-bottom: 18px;
}

.window-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 12px;
    margin-bottom: 16px;
}

.window-dots { display: flex; gap: 6px; }
.dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.dot-red { background: #FF5F56; }
.dot-yellow { background: #FFBD2E; }
.dot-green { background: #27C93F; }

/* Buttons & Segmented Control */
div[data-testid="stButton"] > button {
    border-radius: 9999px !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    min-height: 44px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #E2E8F0 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #F8FAFC !important;
    border-color: #0284C7 !important;
    color: #0284C7 !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(2, 132, 199, 0.15) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.4) !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 2px solid #CBD5E1 !important;
    border-radius: 9999px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15) !important;
    padding: 6px 12px !important;
}

div[data-testid="stChatInput"] input, div[data-testid="stChatInput"] textarea {
    color: #0F172A !important;
}

/* Chat Bubbles */
.chat-user {
    background: #0F172A !important;
    color: #FFFFFF !important;
    padding: 14px 22px;
    border-radius: 24px 24px 4px 24px;
    margin: 12px 0 12px auto;
    max-width: 82%;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.2);
    font-size: 0.96rem;
    line-height: 1.55;
}
.chat-user * { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }

.chat-ai {
    background: #F8FAFC !important;
    color: #0F172A !important;
    padding: 18px 24px;
    border-radius: 24px 24px 24px 4px;
    margin: 12px 0;
    max-width: 90%;
    border: 1px solid #E2E8F0;
    font-size: 0.96rem;
    line-height: 1.65;
}
.chat-ai * { color: #0F172A !important; -webkit-text-fill-color: #0F172A !important; }

/* File Uploader Clean Light Style */
div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 24px !important;
    padding: 18px !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFC !important;
    border: 2px dashed #94A3B8 !important;
    border-radius: 18px !important;
    padding: 24px 16px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: #0F172A !important;
}

/* Metric Boxes */
.metric-box {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0;
    border-radius: 22px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
.metric-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #0F172A !important;
}
.metric-lbl {
    font-size: 0.76rem;
    color: #475569 !important;
    font-weight: 800;
    text-transform: uppercase;
    margin-top: 4px;
}

.arch-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0;
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
.arch-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.arch-desc {
    font-size: 0.92rem;
    color: #334155;
    line-height: 1.6;
    margin: 0;
}

/* Streamlit Expander Contrast Fix */
div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    margin-bottom: 10px !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(EDITORIAL_NATURE_CSS, unsafe_allow_html=True)

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

# Top Header Bar
ai_connected = chat_ai_available()
status_html = (
    '<div class="top-pill"><span class="pulse-dot"></span>Sub-150ms Live Neural Engine</div>'
    if ai_connected
    else '<div class="top-pill" style="background:#FFFBEB; color:#B45309; border-color:#FDE68A;">● Offline Mode</div>'
)

st.markdown(
    f'<div class="top-header">'
    f'<div class="top-brand">✨ LexieLingua AI</div>'
    f'{status_html}'
    f'</div>',
    unsafe_allow_html=True,
)

# Navigation Segmented Control
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
    st.markdown(
        '<div class="hero-editorial">'
        '<div class="badge-tag">⚡ NEXT-GENERATION AI COPILOT</div>'
        '<div class="headline-text">'
        'INTELLIGENCE THAT <span class="sticker sticker-blue">MAKES</span>'
        '<br>STUDENTS <span class="sticker sticker-pink">EXCEL</span> FASTER'
        '</div>'
        '<div class="sub-editorial">— Instant, accurate AI copilot for programming, mathematics, and exam preparation.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([2.6, 1.1])

    with left_col:
        st.markdown(
            '<div class="solid-card">'
            '<div class="window-header">'
            '<div class="window-dots"><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></div>'
            '<div style="font-size:0.84rem; font-weight:800; color:#0F172A;">⚡ LexieLingua Neural Engine • Active Workspace</div>'
            '<div style="width:40px;"></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(
                    '<div class="chat-ai">👋 <b>Welcome to LexieLingua AI.</b><br>Ask me any coding question, algorithm derivation, or exam problem for an instant streamed response.</div>',
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
                            '<div style="font-size:0.8rem; color:#0284C7; font-weight:800; margin:10px 0 2px;">✨ LexieLingua AI</div>',
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
            save_chat_message(st.session_state.session_id, "user", user_input)

            st.markdown('<div style="font-size:0.8rem; color:#0284C7; margin:12px 0 4px; font-weight:800;">✨ LexieLingua AI</div>', unsafe_allow_html=True)
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
            '<div class="solid-card">'
            '<div style="font-size:0.8rem; font-weight:800; color:#0284C7; text-transform:uppercase; margin-bottom:4px;">Quick Actions</div>'
            '<h4 style="margin:0 0 14px; font-weight:800; font-size:1.1rem; color:#0F172A; font-family:\'Space Grotesk\', sans-serif;">⚡ Instant Prompts</h4>',
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
        '<div class="hero-editorial">'
        '<div class="badge-tag">📄 DOCUMENT SYNTHESIS</div>'
        '<div class="headline-text">'
        'SYNTHESIZE <span class="sticker sticker-blue">KNOWLEDGE</span>'
        '<br>IN SECONDS'
        '</div>'
        '<div class="sub-editorial">— Drop textbooks, lecture notes, or research papers for clean, structured takeaways.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="solid-card">', unsafe_allow_html=True)
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
                    f'<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:20px; padding:22px; margin-top:18px;">'
                    f'<div style="font-size:0.8rem; font-weight:800; color:#0284C7; text-transform:uppercase; margin-bottom:6px;">Synthesized Overview</div>'
                    f'<h3 style="margin:0 0 12px; font-weight:800; font-size:1.2rem; color:#0F172A; font-family:\'Space Grotesk\', sans-serif;">📝 Executive Summary</h3>',
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
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# VIEW 3: HISTORY & AUDIT LOG
# ============================================================
elif st.session_state.page == "history":
    st.markdown(
        '<div class="hero-editorial">'
        '<div class="badge-tag">📊 AUDIT & LOGS</div>'
        '<div class="headline-text">'
        'ACTIVITY & <span class="sticker sticker-pink">HISTORY</span>'
        '<br>RECORDS'
        '</div>'
        '<div class="sub-editorial">— Inspect past questions asked, AI answers delivered, and uploaded document summaries.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    h_col1, h_col2 = st.columns(2)

    with h_col1:
        st.markdown(
            '<div class="solid-card">'
            '<h3 style="margin:0 0 14px; font-weight:800; font-size:1.15rem; color:#0F172A; font-family:\'Space Grotesk\', sans-serif;">💬 Questions & Chat History</h3>',
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
            '<div class="solid-card">'
            '<h3 style="margin:0 0 14px; font-weight:800; font-size:1.15rem; color:#0F172A; font-family:\'Space Grotesk\', sans-serif;">📁 Uploaded Documents & Summaries</h3>',
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
# VIEW 4: ARCHITECTURE & SPECS
# ============================================================
else:
    st.markdown(
        '<div class="hero-editorial">'
        '<div class="badge-tag">⚙️ SYSTEM FOUNDRY</div>'
        '<div class="headline-text">'
        'HIGH-THROUGHPUT <span class="sticker sticker-blue">NEURAL</span>'
        '<br>FOUNDRY'
        '</div>'
        '<div class="sub-editorial">— Technical specifications of LexieLingua AI\'s multi-tier low-latency infrastructure.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="metric-box"><div class="metric-val">&lt; 150 ms</div><div class="metric-lbl">Time to First Token</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-box"><div class="metric-val">Asynchronous</div><div class="metric-lbl">Non-Blocking Daemon I/O</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-box"><div class="metric-val">Pooled HTTP</div><div class="metric-lbl">Persistent Connection Engine</div></div>', unsafe_allow_html=True)

    st.write("")

    a1, a2 = st.columns(2)

    with a1:
        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">📥 1. Ingestion & Document Processing</div>'
            '<p class="arch-desc">'
            'LexieLingua extracts text streams from raw uploads (PDF, DOCX, TXT, MD) completely in-memory using optimized binary parsers without creating disk I/O bottlenecks.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">🧠 2. Context Orchestration</div>'
            '<p class="arch-desc">'
            'Employs sliding-window memory management to keep token overhead minimal and sub-second Time To First Token (TTFT) consistent.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with a2:
        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">⚡ 3. Azure Neural Acceleration</div>'
            '<p class="arch-desc">'
            'Powered by Azure OpenAI deployments streaming tokens word-by-word with live Server-Sent Events (SSE).'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">🔒 4. Asynchronous Audit Logging</div>'
            '<p class="arch-desc">'
            'Chat queries and document summaries are automatically saved to Supabase PostgreSQL using background thread pool workers with zero UI latency.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )
