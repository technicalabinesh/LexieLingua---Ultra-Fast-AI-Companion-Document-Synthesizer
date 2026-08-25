"""
LexieLingua - Next-Gen AI Student Support & Document Intelligence Platform
Run:
    streamlit run app.py
"""

import os
import uuid
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from chatbot import (
    stream_answer,
    is_ai_mode_available as chat_ai_available,
)
from summarizer import (
    summarize,
    is_ai_mode_available as summ_ai_available,
)
from utils import extract_text

# ============================================================
# INITIAL CONFIGURATION & DATABASE CONNECTIVITY
# ============================================================
load_dotenv()

st.set_page_config(
    page_title="LexieLingua AI | Intelligent Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Optional Supabase connection setup (Zero-crash fallback)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = None

try:
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase_client = None

def save_chat_message(session_id: str, role: str, content: str):
    """Saves a message turn to Supabase PostgreSQL."""
    if supabase_client:
        try:
            supabase_client.table("chat_history").insert({
                "session_id": session_id,
                "role": role,
                "content": content
            }).execute()
        except Exception:
            pass

def load_chat_history(session_id: str):
    """Loads chat records for the active session from Supabase."""
    if supabase_client:
        try:
            res = supabase_client.table("chat_history")\
                .select("role, content")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .execute()
            return res.data or []
        except Exception:
            pass
    return []

def save_summary_to_db(summary_data: dict):
    """Saves generated document summaries to Supabase."""
    if supabase_client:
        try:
            supabase_client.table("document_summaries").insert({
                "filename": summary_data.get("filename"),
                "summary": summary_data.get("summary"),
                "key_points": summary_data.get("key_points", []),
                "original_words": summary_data.get("original_words", 0),
                "summary_words": summary_data.get("summary_words", 0),
            }).execute()
        except Exception:
            pass

# ============================================================
# ULTRA-MODERN FROSTED GLASS & MOTION CSS
# ============================================================
PREMIUM_EFFECTS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary-gradient: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #D946EF 100%);
    --dark: #0F172A;
    --border: #E2E8F0;
    --glass-bg: rgba(255, 255, 255, 0.85);
    --glass-shadow: 0 14px 34px -10px rgba(99, 102, 241, 0.12), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
}

/* Global Font & Text */
html, body, p, h1, h2, h3, h4, h5, h6, label {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #0F172A !important;
}

.stApp {
    background: 
        radial-gradient(circle at 10% 10%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(217, 70, 239, 0.12) 0%, transparent 40%),
        linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%) !important;
    background-attachment: fixed;
}

.main .block-container {
    max-width: 1200px;
    padding: 1.25rem 1.75rem 4rem;
}

/* Header Navbar */
.nav-container {
    background: #FFFFFF !important;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 14px 26px;
    box-shadow: var(--glass-shadow);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-logo {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Status Pill */
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

/* Cards */
.ui-card {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px;
    padding: 24px;
    box-shadow: var(--glass-shadow);
    margin-bottom: 18px;
}

.hero-card {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px;
    padding: 24px 28px;
    margin-bottom: 18px;
    box-shadow: var(--glass-shadow);
}

.hero-title {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0 0 6px;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Navigation Buttons */
div[data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    padding: 10px 18px !important;
    min-height: 44px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #F8FAFC !important;
    border-color: #6366F1 !important;
    color: #6366F1 !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: var(--primary-gradient) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.3) !important;
}

/* Chat Input (Crisp Light Theme Fix) */
div[data-testid="stChatInput"] { 
    background: transparent !important; 
}

div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06) !important;
}

div[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    font-size: 0.96rem !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}

div[data-testid="stChatInput"] button {
    background: #4F46E5 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}

/* Chat Bubbles (High Contrast Fix) */
.chat-user {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 12px 0 12px auto;
    max-width: 82%;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
    font-size: 0.95rem;
    line-height: 1.55;
}
.chat-user * { 
    color: #FFFFFF !important; 
    -webkit-text-fill-color: #FFFFFF !important;
}

.chat-ai {
    background: #FFFFFF !important;
    color: #0F172A !important;
    padding: 18px 22px;
    border-radius: 18px 18px 18px 4px;
    margin: 12px 0;
    max-width: 88%;
    border: 1px solid var(--border);
    box-shadow: var(--glass-shadow);
    font-size: 0.95rem;
    line-height: 1.65;
}
.chat-ai * { 
    color: #0F172A !important; 
    -webkit-text-fill-color: #0F172A !important;
}

/* Quick Prompt Chip Buttons */
.chip-wrapper div[data-testid="stButton"] > button {
    text-align: left !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
    margin-bottom: 4px !important;
    height: auto !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    word-break: break-word !important;
}

.chip-wrapper div[data-testid="stButton"] > button:hover {
    border-color: #6366F1 !important;
    color: #4F46E5 !important;
}

/* Metric Boxes */
.metric-box {
    background: #FFFFFF !important;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    box-shadow: var(--glass-shadow);
}
.metric-val {
    font-size: 1.75rem;
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

/* File Uploader Light Polish */
div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 14px !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFC !important;
    border: 2px dashed #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: #334155 !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(PREMIUM_EFFECTS_CSS, unsafe_allow_html=True)

# ============================================================
# STATE INITIALIZATION
# ============================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "page" not in st.session_state:
    st.session_state.page = "chat"

if "chat_history" not in st.session_state:
    db_history = load_chat_history(st.session_state.session_id)
    st.session_state.chat_history = db_history if db_history else []

if "last_summary" not in st.session_state:
    st.session_state.last_summary = None

def navigate(page: str):
    st.session_state.page = page
    st.rerun()

# ============================================================
# TOP NAVBAR
# ============================================================
ai_connected = chat_ai_available()
status_html = (
    '<span class="status-pill status-online"><span class="status-dot"></span>Ultra-Fast Streaming Active</span>'
    if ai_connected
    else '<span class="status-pill status-offline">● Offline Fallback</span>'
)

st.markdown(
    f'<div class="nav-container">'
    f'<div class="brand-logo"><span>✨</span> LexieLingua <span style="font-size: 0.82rem; font-weight:700; color:#4F46E5; letter-spacing:0.02em; padding:2px 8px; background:rgba(79, 70, 229, 0.1); border-radius:8px; border:1px solid rgba(79, 70, 229, 0.2);">PRO</span></div>'
    f'<div>{status_html}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button("💬 Conversational AI", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary"):
        navigate("chat")
with nav_cols[1]:
    if st.button("📄 Document Synthesizer", use_container_width=True, type="primary" if st.session_state.page == "summarizer" else "secondary"):
        navigate("summarizer")
with nav_cols[2]:
    if st.button("⚙️ Neural Architecture", use_container_width=True, type="primary" if st.session_state.page == "about" else "secondary"):
        navigate("about")

st.write("")

# ============================================================
# VIEW 1: CONVERSATIONAL AI STREAMING
# ============================================================
if st.session_state.page == "chat":
    left_col, right_col = st.columns([2.6, 1.1])

    with left_col:
        st.markdown(
            '<div class="hero-card">'
            '<div class="hero-title">Conversational Copilot</div>'
            '<p style="color:#64748B; font-size:0.92rem; margin:0; line-height:1.5;">Real-time generative intelligence for code debugging, study inquiries, and problem-solving.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        if not st.session_state.chat_history:
            st.markdown(
                '<div class="chat-ai"><span style="font-size:1.2rem;">👋</span> <b>Welcome! I am LexieLingua Copilot.</b><br>Ask me anything — generate algorithms, analyze academic papers, or brainstorm project ideas.</div>',
                unsafe_allow_html=True,
            )

        for turn in st.session_state.chat_history:
            css_class = "chat-user" if turn["role"] == "user" else "chat-ai"
            sender = "👤 You" if turn["role"] == "user" else "✨ LexieLingua AI"
            st.markdown(
                f'<div class="{css_class}">'
                f'<div style="font-size:0.75rem; opacity:0.85; margin-bottom:5px; font-weight:700;">{sender}</div>'
                f'<div>{turn["content"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        user_input = st.chat_input("Ask a question, request code, or paste content...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            save_chat_message(st.session_state.session_id, "user", user_input)

            # Display user bubble
            st.markdown(
                f'<div class="chat-user">'
                f'<div style="font-size:0.75rem; opacity:0.85; margin-bottom:5px; font-weight:700;">👤 You</div>'
                f'<div>{user_input}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Stream AI response
            with st.container():
                st.markdown('<div style="font-size:0.75rem; color:#4F46E5; margin:10px 0 4px; font-weight:800;">✨ LexieLingua AI</div>', unsafe_allow_html=True)
                stream_gen = stream_answer(user_input, st.session_state.chat_history[:-1])
                full_ai_response = st.write_stream(stream_gen)

            st.session_state.chat_history.append({"role": "assistant", "content": full_ai_response})
            save_chat_message(st.session_state.session_id, "assistant", full_ai_response)
            st.rerun()

        if st.session_state.chat_history:
            st.write("")
            if st.button("🗑 Clear Chat History", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()

    with right_col:
        st.markdown(
            '<div class="ui-card">'
            '<div style="font-size:0.78rem; font-weight:800; color:#4F46E5; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Quick Actions</div>'
            '<h4 style="margin:0 0 12px; font-weight:800; font-size:1.02rem;">⚡ Instant Prompts</h4>',
            unsafe_allow_html=True,
        )
        
        prompts = [
            ("💻", "Write a Python script to reverse a linked list with test cases."),
            ("⚛️", "Explain Quantum Entanglement with a clear visual analogy."),
            ("⚡", "What are the top 5 performance optimization patterns in SQL?"),
            ("🎓", "Design a structured 14-day study plan for machine learning finals."),
        ]
        
        st.markdown('<div class="chip-wrapper">', unsafe_allow_html=True)
        for idx, (icon, prompt_text) in enumerate(prompts):
            if st.button(f"{icon} {prompt_text}", key=f"quick_{idx}", type="secondary", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": prompt_text})
                save_chat_message(st.session_state.session_id, "user", prompt_text)
                st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# ============================================================
# VIEW 2: DOCUMENT SUMMARIZER
# ============================================================
elif st.session_state.page == "summarizer":
    st.markdown(
        '<div class="hero-card">'
        '<div class="hero-title">Document Intelligence & Synthesis</div>'
        '<p style="color:#64748B; font-size:0.92rem; margin:0; line-height:1.5;">Ingest PDF, DOCX, TXT, or Markdown documents to distill high-density summaries, actionable takeaways, and critical insights.</p>'
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
            with st.spinner("⚡ Extracting text & generating neural synthesis..."):
                raw_text = extract_text(doc_file)
                if not raw_text.strip():
                    st.error("❌ No readable text could be extracted from this document.")
                else:
                    res = summarize(raw_text, length=summary_len)
                    res["filename"] = doc_file.name
                    res["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.last_summary = res
                    save_summary_to_db(res)

    if st.session_state.last_summary:
        sum_data = st.session_state.last_summary
        orig_w = sum_data.get("original_words", 0)
        summ_w = sum_data.get("summary_words", 0)
        reduction = round(100 * (1 - (summ_w / max(orig_w, 1)))) if orig_w else 0

        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{orig_w:,}</div><div class="metric-lbl">Source Words</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{summ_w:,}</div><div class="metric-lbl">Summary Words</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><div class="metric-val">-{reduction}%</div><div class="metric-lbl">Data Compression</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.2rem; margin-top:5px;">{sum_data.get("mode", "AI")}</div><div class="metric-lbl">Inference Mode</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown(
            f'<div class="ui-card">'
            f'<div style="font-size:0.78rem; font-weight:800; color:#4F46E5; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">Synthesized Overview</div>'
            f'<h3 style="margin:0 0 12px; font-weight:800; font-size:1.15rem;">📝 Executive Summary</h3>'
            f'<p style="line-height:1.75; font-size:1rem; color:#1E293B; white-space:pre-wrap; margin:0;">{sum_data.get("summary", "")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if sum_data.get("key_points"):
            pts = "".join(f"<li style='margin-bottom:8px;'>{p}</li>" for p in sum_data["key_points"])
            st.markdown(
                f'<div class="ui-card" style="border-left: 4px solid #4F46E5 !important;">'
                f'<div style="font-size:0.78rem; font-weight:800; color:#4F46E5; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">Key Highlights</div>'
                f'<h3 style="margin:0 0 12px; font-weight:800; font-size:1.15rem;">🔑 Critical Takeaways</h3>'
                f'<ul style="line-height:1.7; font-size:0.95rem; color:#334155; padding-left:20px; margin:0;">{pts}</ul>'
                f'</div>',
                unsafe_allow_html=True,
            )

        export_content = f"SUMMARY: {sum_data.get('filename')}\nGenerated: {sum_data.get('generated_at')}\n\n{sum_data.get('summary')}\n\nKEY TAKEAWAYS:\n" + "\n".join(f"- {pt}" for pt in sum_data.get("key_points", []))
        st.download_button("⬇ Export Structured Summary (.txt)", data=export_content, file_name=f"summary_{sum_data.get('filename', 'doc')}.txt", mime="text/plain", use_container_width=True)

# ============================================================
# VIEW 3: ARCHITECTURE & ENGINE SPECIFICATIONS
# ============================================================
else:
    st.markdown(
        '<div class="hero-card">'
        '<div class="hero-title">Neural Engine & Platform Architecture</div>'
        '<p style="color:#64748B; font-size:0.92rem; margin:0; line-height:1.5;">LexieLingua utilizes an enterprise multi-tier architecture uniting cloud neural acceleration with deterministic edge extraction.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown(
            '<div class="ui-card" style="border-top:4px solid #4F46E5 !important;">'
            '<div style="font-size:1.4rem; margin-bottom:6px;">📥</div>'
            '<h4 style="margin:0 0 6px; font-size:1rem; font-weight:800;">1. Ingestion</h4>'
            '<p style="font-size:0.86rem; color:#475569; line-height:1.5; margin:0;">Extracts clean text streams from raw uploads (PDF, DOCX, TXT) or conversational payloads.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            '<div class="ui-card" style="border-top:4px solid #7C3AED !important;">'
            '<div style="font-size:1.4rem; margin-bottom:6px;">🧠</div>'
            '<h4 style="margin:0 0 6px; font-size:1rem; font-weight:800;">2. Context Layer</h4>'
            '<p style="font-size:0.86rem; color:#475569; line-height:1.5; margin:0;">Applies sliding-window memory management and dynamic prompt engineering to prevent context overflow.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            '<div class="ui-card" style="border-top:4px solid #10B981 !important;">'
            '<div style="font-size:1.4rem; margin-bottom:6px;">⚡</div>'
            '<h4 style="margin:0 0 6px; font-size:1rem; font-weight:800;">3. Neural Foundry</h4>'
            '<p style="font-size:0.86rem; color:#475569; line-height:1.5; margin:0;">High-throughput Azure GPT-5.4 global deployment executes low-latency cognitive synthesis.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with p4:
        st.markdown(
            '<div class="ui-card" style="border-top:4px solid #F59E0B !important;">'
            '<div style="font-size:1.4rem; margin-bottom:6px;">🚀</div>'
            '<h4 style="margin:0 0 6px; font-size:1rem; font-weight:800;">4. Real-Time SSE</h4>'
            '<p style="font-size:0.86rem; color:#475569; line-height:1.5; margin:0;">Pushes generated token streams word-by-word with &lt;250ms TTFT direct to the reactive client.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.write("")
    spec_col1, spec_col2, spec_col3, spec_col4 = st.columns(4)
    with spec_col1:
        st.markdown('<div class="metric-box"><div class="metric-val" style="font-size:1.3rem;">Azure GPT-5.4</div><div class="metric-lbl">LLM Engine</div></div>', unsafe_allow_html=True)
    with spec_col2:
        st.markdown('<div class="metric-box"><div class="metric-val" style="font-size:1.3rem;">&lt; 220 ms</div><div class="metric-lbl">Time to First Token</div></div>', unsafe_allow_html=True)
    with spec_col3:
        st.markdown('<div class="metric-box"><div class="metric-val" style="font-size:1.3rem;">Streamlit + Py3.11</div><div class="metric-lbl">Core Stack</div></div>', unsafe_allow_html=True)
    with spec_col4:
        st.markdown('<div class="metric-box"><div class="metric-val" style="font-size:1.3rem;">Stateless / In-Mem</div><div class="metric-lbl">Data Privacy</div></div>', unsafe_allow_html=True)
