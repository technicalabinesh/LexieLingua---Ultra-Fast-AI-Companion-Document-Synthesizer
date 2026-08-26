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
    page_title="LexieLingua AI | Intelligence That Makes Learning Alive",
    page_icon="🌿",
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
# EDITORIAL NATURE & LIQUID GLASS CSS
# ============================================================
EDITORIAL_NATURE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --glass-bg: rgba(255, 255, 255, 0.72);
    --glass-card: rgba(255, 255, 255, 0.88);
    --glass-border: rgba(255, 255, 255, 0.65);
    --shadow-ambient: 0 30px 60px -12px rgba(15, 23, 42, 0.18), 0 18px 36px -18px rgba(0, 0, 0, 0.12);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

/* Scenic Landscape Backdrop with Soft Tint */
.stApp {
    background: 
        linear-gradient(180deg, rgba(8, 20, 32, 0.15) 0%, rgba(240, 253, 244, 0.35) 60%, rgba(236, 253, 245, 0.65) 100%),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2832&auto=format&fit=crop") no-repeat center center fixed !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}

.main .block-container {
    max-width: 1280px;
    padding: 1.4rem 2rem 4.5rem;
}

/* Minimalist Frosted Top Header */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 9999px;
    padding: 12px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
}

.top-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #0F172A;
    text-transform: uppercase;
}

.top-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 800;
    background: rgba(255, 255, 255, 0.85);
    color: #15803D;
    border: 1px solid rgba(255, 255, 255, 0.95);
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background: #22C55E;
    border-radius: 50%;
    box-shadow: 0 0 10px #22C55E;
}

/* Giant Editorial Hero Section */
.hero-editorial {
    padding: 20px 0 34px;
    position: relative;
}

.author-chip {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.85);
    border-radius: 20px;
    padding: 10px 18px;
    margin-bottom: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.06);
}

.headline-container {
    margin: 10px 0 16px;
    position: relative;
}

.headline-text {
    font-family: 'Space Grotesk', -apple-system, sans-serif;
    font-size: 3.8rem;
    font-weight: 900;
    line-height: 1.04;
    letter-spacing: -0.04em;
    color: #FFFFFF;
    text-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    text-transform: uppercase;
}

/* Playful Floating Sticker Badges */
.sticker {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 0.95rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    vertical-align: middle;
    margin: 0 8px;
}
.sticker-blue {
    background: #38BDF8;
    color: #082F49;
    transform: rotate(-3deg);
}
.sticker-pink {
    background: #F472B6;
    color: #831843;
    transform: rotate(3deg);
}
.sticker-purple {
    background: #C084FC;
    color: #3B0764;
    transform: rotate(-2deg);
}

.sub-editorial {
    font-size: 1.15rem;
    color: #FFFFFF;
    font-weight: 600;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    max-width: 650px;
    line-height: 1.5;
    margin-bottom: 12px;
}

/* Translucent Glass Card Wrapper */
.glass-container {
    background: var(--glass-card) !important;
    backdrop-filter: blur(32px) !important;
    -webkit-backdrop-filter: blur(32px) !important;
    border: 1.5px solid var(--glass-border) !important;
    border-radius: 32px !important;
    padding: 26px 30px !important;
    box-shadow: var(--shadow-ambient) !important;
    margin-bottom: 20px;
}

.ui-card {
    background: rgba(255, 255, 255, 0.82) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    margin-bottom: 16px;
}

/* Nav & Action Buttons */
div[data-testid="stButton"] > button {
    border-radius: 9999px !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    min-height: 46px !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(16px) !important;
    color: #0F172A !important;
    border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #FFFFFF !important;
    border-color: #38BDF8 !important;
    color: #0284C7 !important;
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(56, 189, 248, 0.25) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.3) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px);
    background: #1E293B !important;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.4) !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] > div {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
    border-radius: 9999px !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12) !important;
    padding: 6px 12px !important;
}

.chat-user {
    background: #0F172A !important;
    color: #FFFFFF !important;
    padding: 14px 22px;
    border-radius: 24px 24px 4px 24px;
    margin: 12px 0 12px auto;
    max-width: 82%;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);
    font-size: 0.96rem;
    line-height: 1.55;
}
.chat-user * { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }

.chat-ai {
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(16px) !important;
    color: #0F172A !important;
    padding: 18px 24px;
    border-radius: 24px 24px 24px 4px;
    margin: 12px 0;
    max-width: 90%;
    border: 1px solid rgba(255, 255, 255, 0.95);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    font-size: 0.96rem;
    line-height: 1.65;
}

/* Clean Frosted File Uploader */
div[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: 24px !important;
    padding: 18px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF !important;
    border: 2px dashed #94A3B8 !important;
    border-radius: 18px !important;
    padding: 24px 16px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: #1E293B !important;
}

.metric-box {
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.95);
    border-radius: 24px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
}
.metric-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 900;
    color: #0F172A;
}
.metric-lbl {
    font-size: 0.75rem;
    color: #475569 !important;
    font-weight: 800;
    text-transform: uppercase;
    margin-top: 2px;
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
    else '<div class="top-pill" style="color:#B45309;">● Offline Mode</div>'
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
# VIEW 1: CONVERSATIONAL AI (EDITORIAL NATURE)
# ============================================================
if st.session_state.page == "chat":
    st.markdown(
        '<div class="hero-editorial">'
        '<div class="author-chip">'
        '<span style="font-size:1.1rem;">🌿</span>'
        '<span style="font-size:0.85rem; font-weight:800; color:#0F172A;">AVAILABLE 24/7 • STUDENT COPILOT</span>'
        '</div>'
        '<div class="headline-container">'
        '<div class="headline-text">'
        'INTELLIGENCE THAT <span class="sticker sticker-blue">MAKES</span>'
        '<br>STUDENTS <span class="sticker sticker-pink">EXCEL</span> FASTER'
        '</div>'
        '</div>'
        '<div class="sub-editorial">— Not just an assistant. An AI companion that makes studying feel alive, instant, and effortless.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([2.6, 1.1])

    with left_col:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(
                    '<div class="chat-ai">👋 <b>Welcome! I am LexieLingua AI.</b><br>Ask me any coding algorithm, math derivation, or exam question for an instant answer.</div>',
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
                            '<div style="font-size:0.78rem; color:#0284C7; font-weight:800; margin:8px 0 2px;">✨ LexieLingua AI</div>',
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

            st.markdown('<div style="font-size:0.78rem; color:#0284C7; margin:12px 0 4px; font-weight:800;">✨ LexieLingua AI</div>', unsafe_allow_html=True)
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
            '<div class="glass-container">'
            '<div style="font-size:0.78rem; font-weight:900; color:#0284C7; text-transform:uppercase; margin-bottom:4px;">Quick Actions</div>'
            '<h4 style="margin:0 0 14px; font-weight:900; font-size:1.1rem; font-family:\'Space Grotesk\', sans-serif;">⚡ INSTANT PROMPTS</h4>',
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
        '<div class="headline-container">'
        '<div class="headline-text">'
        'SYNTHESIZE <span class="sticker sticker-purple">KNOWLEDGE</span>'
        '<br>IN SECONDS'
        '</div>'
        '</div>'
        '<div class="sub-editorial">— Drop textbooks, lecture notes, or research papers for clean, structured takeaways.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    up_col, opt_col = st.columns([2.2, 1])
    with up_col:
        doc_file = st.file_uploader("Upload document", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
    with opt_col:
        summary_len = st.select_slider("Target Detail", options=["Short", "Medium", "Long"], value="Medium")
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
                    f'<div style="font-size:0.78rem; font-weight:800; color:#0284C7; text-transform:uppercase; margin-bottom:6px;">Synthesized Overview</div>'
                    f'<h3 style="margin:0 0 12px; font-weight:900; font-size:1.2rem; font-family:\'Space Grotesk\', sans-serif;">📝 Executive Summary</h3>',
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
        '<div class="headline-container">'
        '<div class="headline-text">'
        'ACTIVITY & <span class="sticker sticker-pink">HISTORY</span>'
        '<br>RECORDS'
        '</div>'
        '</div>'
        '<div class="sub-editorial">— Inspect questions asked, AI answers delivered, and uploaded summaries.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    h_col1, h_col2 = st.columns(2)

    with h_col1:
        st.markdown(
            '<div class="glass-container">'
            '<h3 style="margin:0 0 14px; font-weight:900; font-size:1.15rem; font-family:\'Space Grotesk\', sans-serif;">💬 Questions & Chat History</h3>',
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
            '<div class="glass-container">'
            '<h3 style="margin:0 0 14px; font-weight:900; font-size:1.15rem; font-family:\'Space Grotesk\', sans-serif;">📁 Uploaded Documents & Summaries</h3>',
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
        '<div class="headline-container">'
        '<div class="headline-text">'
        'HIGH-THROUGHPUT <span class="sticker sticker-blue">NEURAL</span>'
        '<br>FOUNDRY'
        '</div>'
        '</div>'
        '<div class="sub-editorial">— Persistent HTTP connection pooling and non-blocking asynchronous threads for instant token delivery.</div>'
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
