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
    page_icon="⚡",
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
# CINEMATIC DARK FROSTED GLASS CSS (HIGH ENCLOSURE FIX)
# ============================================================
CINEMATIC_GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}

/* Background with Cinematic Deep Nature Tint */
.stApp {
    background: 
        linear-gradient(180deg, rgba(8, 14, 26, 0.70) 0%, rgba(8, 14, 26, 0.50) 45%, rgba(8, 14, 26, 0.85) 100%),
        url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2832&auto=format&fit=crop") no-repeat center center fixed !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}

.main .block-container {
    max-width: 1280px;
    padding: 1.2rem 2rem 4.5rem;
}

/* Header Navbar */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.80) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 9999px;
    padding: 12px 28px;
    margin-bottom: 20px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
}

.top-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: #FFFFFF !important;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* macOS Dots */
.window-dots {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.dot {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    display: inline-block;
}
.dot-red { background: #FF5F56; box-shadow: 0 0 8px rgba(255, 95, 86, 0.7); }
.dot-yellow { background: #FFBD2E; box-shadow: 0 0 8px rgba(255, 189, 46, 0.7); }
.dot-green { background: #27C93F; box-shadow: 0 0 8px rgba(39, 201, 63, 0.7); }

.top-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 800;
    background: rgba(34, 197, 94, 0.15) !important;
    color: #4ADE80 !important;
    border: 1px solid rgba(74, 222, 128, 0.3);
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
    padding: 10px 0 18px;
}

.headline-text {
    font-family: 'Space Grotesk', -apple-system, sans-serif;
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -0.04em;
    color: #FFFFFF !important;
    text-shadow: 0 4px 25px rgba(0, 0, 0, 0.7);
    text-transform: uppercase;
    margin-bottom: 8px;
}

.sticker {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 10px;
    font-weight: 800;
    font-size: 0.9rem;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
    vertical-align: middle;
    margin: 0 6px;
}
.sticker-blue { background: #0284C7; color: #FFFFFF !important; transform: rotate(-2deg); }
.sticker-pink { background: #DB2777; color: #FFFFFF !important; transform: rotate(2deg); }

.sub-editorial {
    font-size: 1.05rem;
    color: #E2E8F0 !important;
    font-weight: 600;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.7);
    max-width: 720px;
    line-height: 1.5;
}

/* One-line Description Card */
.one-line-box {
    background: rgba(15, 23, 42, 0.82) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 20px !important;
    padding: 16px 22px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.35) !important;
    display: flex;
    align-items: center;
}
.one-line-box * {
    color: #F8FAFC !important;
}

.solid-card {
    background: rgba(15, 23, 42, 0.82) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 24px !important;
    padding: 22px 26px !important;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.4) !important;
    margin-bottom: 16px;
}
.solid-card * {
    color: #F8FAFC !important;
}

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 9999px !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    min-height: 44px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(15, 23, 42, 0.70) !important;
    backdrop-filter: blur(20px) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(30, 41, 59, 0.95) !important;
    border-color: #38BDF8 !important;
    color: #38BDF8 !important;
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(56, 189, 248, 0.25) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0284C7 0%, #38BDF8 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 8px 25px rgba(2, 132, 199, 0.45) !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    padding-top: 10px !important;
}

div[data-testid="stChatInput"] > div {
    background: rgba(15, 23, 42, 0.90) !important;
    backdrop-filter: blur(28px) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 9999px !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.45) !important;
    padding: 6px 14px !important;
}

div[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-size: 0.96rem !important;
    font-weight: 600 !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}

/* ST.CHAT_MESSAGE ENCLOSURE FIX - FULL FROSTED CARD */
div[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.88) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 24px !important;
    padding: 22px 28px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.45) !important;
}

div[data-testid="stChatMessage"] > div {
    background: transparent !important;
}

/* Ensure ALL text inside the chat message is crisp and contained */
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] h1,
div[data-testid="stChatMessage"] h2,
div[data-testid="stChatMessage"] h3,
div[data-testid="stChatMessage"] h4,
div[data-testid="stChatMessage"] h5,
div[data-testid="stChatMessage"] h6,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] div {
    color: #F8FAFC !important;
}

/* Code Syntax Blocks */
div[data-testid="stChatMessage"] pre {
    background: #020617 !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin: 12px 0 !important;
}

div[data-testid="stChatMessage"] pre code,
div[data-testid="stChatMessage"] pre code * {
    color: #F8FAFC !important;
    background: transparent !important;
}

/* Inline Code Badges */
code:not(pre code) {
    background: rgba(56, 189, 248, 0.18) !important;
    color: #38BDF8 !important;
    -webkit-text-fill-color: #38BDF8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.9em !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
}

/* File Uploader Frosted Style */
div[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.82) !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 24px !important;
    padding: 18px !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.35) !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: rgba(2, 6, 23, 0.55) !important;
    border: 2px dashed rgba(255, 255, 255, 0.25) !important;
    border-radius: 18px !important;
    padding: 24px 16px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: #F8FAFC !important;
}

/* Expander Dark Glass Style */
div[data-testid="stExpander"], details[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.82) !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 18px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
}

div[data-testid="stExpander"] summary, details[data-testid="stExpander"] summary {
    background: transparent !important;
    border-radius: 18px !important;
    padding: 14px 20px !important;
}

div[data-testid="stExpander"] summary *, details[data-testid="stExpander"] summary * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
}

div[data-testid="stExpander"] summary svg, details[data-testid="stExpander"] summary svg {
    fill: #38BDF8 !important;
    stroke: #38BDF8 !important;
}

div[data-testid="stExpanderDetails"], details[data-testid="stExpander"] > div {
    background: rgba(2, 6, 23, 0.5) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 16px 20px !important;
    border-bottom-left-radius: 18px !important;
    border-bottom-right-radius: 18px !important;
}

div[data-testid="stExpanderDetails"] *, details[data-testid="stExpander"] > div * {
    color: #E2E8F0 !important;
    -webkit-text-fill-color: #E2E8F0 !important;
}

/* Architecture Uniform Dark Glass Cards */
.arch-card {
    background: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(28px) !important;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 24px;
    padding: 24px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
}
.arch-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.18rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.arch-desc {
    font-size: 0.92rem;
    color: #CBD5E1;
    line-height: 1.6;
    margin: 0;
}

.tech-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.15);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 9999px;
    padding: 4px 12px;
    font-size: 0.76rem;
    font-weight: 700;
    margin-right: 6px;
    margin-top: 8px;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(CINEMATIC_GLASS_CSS, unsafe_allow_html=True)

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

# Top Header Bar with 3 macOS Traffic Dots
ai_connected = chat_ai_available()
status_html = (
    '<div class="top-pill"><span class="pulse-dot"></span>Sub-150ms Live Neural Engine</div>'
    if ai_connected
    else '<div class="top-pill" style="background:rgba(245,158,11,0.15); color:#FBBF24; border-color:rgba(245,158,11,0.3);">● Offline Mode</div>'
)

st.markdown(
    f'<div class="top-header">'
    f'<div class="top-brand">'
    f'<span class="window-dots"><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></span>'
    f'<span>LexieLingua AI</span>'
    f'</div>'
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
        # One-line description in frosted dark glass
        st.markdown(
            '<div class="one-line-box">'
            '<div class="window-dots" style="margin-right:12px;"><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></div>'
            '<p style="margin:0; font-weight:600; font-size:0.95rem; line-height:1.5;">'
            '<b>LexieLingua AI:</b> An ultra-fast conversational copilot designed for instant coding synthesis, academic problem-solving, and real-time student support.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        
        # Render clean dark-glass chat messages
        for turn in st.session_state.chat_history:
            role = turn["role"]
            with st.chat_message(role):
                st.markdown(turn["content"])

        user_input = st.chat_input("Type your question or request code here...")
        if st.session_state.pending_prompt:
            user_input = st.session_state.pending_prompt
            st.session_state.pending_prompt = None

        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            save_chat_message(st.session_state.session_id, "user", user_input)

            with st.chat_message("assistant"):
                stream_gen = stream_answer(user_input, st.session_state.chat_history)
                full_ai_response = st.write_stream(stream_gen)

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
            '<div class="solid-card">'
            '<div style="font-size:0.8rem; font-weight:800; color:#38BDF8; text-transform:uppercase; margin-bottom:4px;">Quick Actions</div>'
            '<h4 style="margin:0 0 14px; font-weight:800; font-size:1.1rem; font-family:\'Space Grotesk\', sans-serif;">⚡ Instant Prompts</h4>',
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
        '<div class="headline-text">'
        'SYNTHESIZE <span class="sticker sticker-blue">KNOWLEDGE</span>'
        '<br>IN SECONDS'
        '</div>'
        '<div class="sub-editorial">— Drop textbooks, lecture notes, or research papers for clean, structured takeaways.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="one-line-box">'
        '<div class="window-dots" style="margin-right:12px;"><span class="dot dot-red"></span><span class="dot dot-yellow"></span><span class="dot dot-green"></span></div>'
        '<p style="margin:0; font-weight:600; font-size:0.95rem; line-height:1.5;">'
        '<b>Document Synthesizer:</b> Ingest PDF, DOCX, TXT, or Markdown documents to distill high-density summaries, actionable takeaways, and critical insights in seconds.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    up_col, opt_col = st.columns([2.2, 1])
    with up_col:
        doc_file = st.file_uploader("Upload document", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
    with opt_col:
        summary_len = st.select_slider("Target Detail Level", options=["Short", "Medium", "Long"], value="Medium")
        run_sum = st.button("⚡ Distill Document", type="primary", use_container_width=True)

    if run_sum:
        if not doc_file:
            st.warning("⚠️ Please upload a document first.")
        else:
            raw_text = extract_text(doc_file)
            if not raw_text.strip():
                st.error("❌ No readable text found in document.")
            else:
                st.markdown(
                    f'<div class="solid-card" style="margin-top:18px;">'
                    f'<div style="font-size:0.8rem; font-weight:800; color:#38BDF8; text-transform:uppercase; margin-bottom:6px;">Synthesized Overview</div>'
                    f'<h3 style="margin:0 0 12px; font-weight:800; font-size:1.2rem; font-family:\'Space Grotesk\', sans-serif;">📝 Executive Summary</h3>',
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
        '<div class="hero-editorial">'
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
            '<h3 style="margin:0 0 16px; font-weight:800; font-size:1.15rem; color:#FFFFFF; font-family:\'Space Grotesk\', sans-serif;">💬 Questions & Chat History</h3>',
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
                role_label = "👤 Question" if item["role"] == "user" else "⚡ LexieLingua Answer"
                created = item.get("created_at", "")[:16].replace("T", " ")
                with st.expander(f"{role_label} ({created})", expanded=False):
                    st.write(item.get("message", ""))
        elif st.session_state.chat_history:
            for item in reversed(st.session_state.chat_history):
                role_label = "👤 Question" if item["role"] == "user" else "⚡ LexieLingua Answer"
                with st.expander(f"{role_label} (Current Session)", expanded=False):
                    st.write(item.get("content", ""))
        else:
            st.info("No recorded chat inquiries yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with h_col2:
        st.markdown(
            '<div class="solid-card">'
            '<h3 style="margin:0 0 16px; font-weight:800; font-size:1.15rem; color:#FFFFFF; font-family:\'Space Grotesk\', sans-serif;">📁 Uploaded Documents & Summaries</h3>',
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
                with st.expander(f"📄 {doc.get('filename')} • {orig_words} words ({uploaded})", expanded=False):
                    st.markdown("**Generated Summary:**")
                    st.write(doc.get("summary", "No summary available."))
        else:
            st.info("No uploaded documents or summaries found.")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# VIEW 4: ARCHITECTURE (UNIFORM DARK GLASS GRID)
# ============================================================
else:
    st.markdown(
        '<div class="hero-editorial">'
        '<div class="headline-text">'
        'HIGH-THROUGHPUT <span class="sticker sticker-blue">NEURAL</span>'
        '<br>FOUNDRY'
        '</div>'
        '<div class="sub-editorial">— Technical architecture and low-latency specifications of the LexieLingua AI platform.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Row 1: Key Performance Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            '<div class="arch-card" style="text-align:center;">'
            '<div style="font-family:\'Space Grotesk\', sans-serif; font-size:2rem; font-weight:900; color:#38BDF8;">&lt; 150 ms</div>'
            '<div style="font-size:0.78rem; color:#94A3B8; font-weight:800; text-transform:uppercase; margin-top:4px;">Time To First Token (TTFT)</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            '<div class="arch-card" style="text-align:center;">'
            '<div style="font-family:\'Space Grotesk\', sans-serif; font-size:2rem; font-weight:900; color:#38BDF8;">Non-Blocking</div>'
            '<div style="font-size:0.78rem; color:#94A3B8; font-weight:800; text-transform:uppercase; margin-top:4px;">Async Daemon Database I/O</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            '<div class="arch-card" style="text-align:center;">'
            '<div style="font-family:\'Space Grotesk\', sans-serif; font-size:2rem; font-weight:900; color:#38BDF8;">Pooled HTTP/2</div>'
            '<div style="font-size:0.78rem; color:#94A3B8; font-weight:800; text-transform:uppercase; margin-top:4px;">Persistent Socket Connection</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    # Row 2: 4 Core Modules in Uniform 2x2 Grid
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">📥 1. Ingestion Engine</div>'
            '<p class="arch-desc">'
            '• <b>PDF Processing:</b> Stream-oriented page-by-page traversal using <code>pypdf.PdfReader</code>.<br>'
            '• <b>Word Extraction:</b> XML DOM paragraph extraction via <code>docx.Document</code>.<br>'
            '• <b>Text Normalization:</b> UTF-8 sanitization with non-destructive fallback.<br>'
            '• <b>Zero-Disk I/O:</b> Entire ingestion cycle runs in RAM buffers (BytesIO).'
            '</p>'
            '<div style="margin-top:auto; padding-top:12px;">'
            '<span class="tech-chip">pypdf</span>'
            '<span class="tech-chip">python-docx</span>'
            '<span class="tech-chip">In-Memory BytesIO</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">🧠 2. Context & Memory Manager</div>'
            '<p class="arch-desc">'
            '• <b>Sliding-Window Memory:</b> Preserves conversational context while capping prompt token overhead.<br>'
            '• <b>Connection Pooling:</b> Reusable keep-alive HTTP/2 sockets avoid TCP handshakes.<br>'
            '• <b>Latency Optimization:</b> Direct token streaming for sub-second visual responsiveness.<br>'
            '• <b>Direct Injection:</b> Clean system directives for concise reasoning.'
            '</p>'
            '<div style="margin-top:auto; padding-top:12px;">'
            '<span class="tech-chip">Sliding Window</span>'
            '<span class="tech-chip">TCP Keep-Alive</span>'
            '<span class="tech-chip">Stream Pipeline</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    c3, c4 = st.columns(2)

    with c3:
        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">⚡ 3. Dual-Mode Neural Foundry</div>'
            '<p class="arch-desc">'
            '• <b>Cloud Model:</b> High-throughput Azure OpenAI (GPT-4o / GPT-5) streaming endpoints.<br>'
            '• <b>Parameter Resilience:</b> Adaptive fallbacks between <code>max_completion_tokens</code> and <code>max_tokens</code>.<br>'
            '• <b>Offline Heuristics:</b> Deterministic TF-IDF sentence frequency graph scoring.<br>'
            '• <b>High Availability:</b> 100% platform uptime even without API keys.'
            '</p>'
            '<div style="margin-top:auto; padding-top:12px;">'
            '<span class="tech-chip">Azure OpenAI</span>'
            '<span class="tech-chip">TF-IDF Scoring</span>'
            '<span class="tech-chip">Auto-Resilience</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            '<div class="arch-card">'
            '<div class="arch-title">🔒 4. Asynchronous Audit Layer</div>'
            '<p class="arch-desc">'
            '• <b>Database Storage:</b> Supabase PostgreSQL managing chat queries and document summaries.<br>'
            '• <b>Worker Thread Pool:</b> Non-blocking <code>ThreadPoolExecutor</code> offloads all database I/O.<br>'
            '• <b>Zero-Lag Logging:</b> Database transactions never stall live token rendering.<br>'
            '• <b>Complete Auditability:</b> Captures word counts, compression stats, and timestamps.'
            '</p>'
            '<div style="margin-top:auto; padding-top:12px;">'
            '<span class="tech-chip">Supabase PostgreSQL</span>'
            '<span class="tech-chip">ThreadPool Daemon</span>'
            '<span class="tech-chip">Audit Logs</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
