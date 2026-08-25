"""
LexieLingua - Next-Gen AI Student Support & Document Intelligence Platform
Run:
    streamlit run app.py
"""

import os
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
# INITIAL CONFIGURATION
# ============================================================
load_dotenv()

st.set_page_config(
    page_title="LexieLingua Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# HUMAN-CRAFTED MINIMALIST SAAS DESIGN (LINEAR / VERCEL STYLE)
# ============================================================
PRODUCTION_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #F8FAFC;
    --surface: #FFFFFF;
    --border: #E2E8F0;
    --border-hover: #CBD5E1;
    --text-primary: #0F172A;
    --text-secondary: #475569;
    --text-muted: #94A3B8;
    --accent: #4338CA;
    --accent-hover: #3730A3;
    --accent-light: #EEF2FF;
    --accent-border: #C7D2FE;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
}

/* Base Reset & Typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
}

.stApp {
    background-color: var(--bg-main) !important;
}

.main .block-container {
    max-width: 1140px;
    padding: 1.5rem 1.5rem 4rem;
}

/* Top App Header */
.app-header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-sm);
}

.app-brand {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.app-brand-badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 6px;
    background: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
    letter-spacing: 0.03em;
}

.app-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
}

.status-live {
    background: #F0FDF4;
    color: #166534;
    border: 1px solid #BBF7D0;
}

.status-dot-live {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #22C55E;
}

.status-fallback {
    background: #FFFBEB;
    color: #92400E;
    border: 1px solid #FDE68A;
}

.status-dot-fallback {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #F59E0B;
}

/* Tab Segment Controls */
div[data-testid="stHorizontalBlock"]:has(button) {
    background: transparent;
    gap: 8px;
    margin-bottom: 18px;
}

div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    min-height: 38px !important;
    padding: 6px 14px !important;
    transition: all 0.15s ease !important;
    border: 1px solid transparent !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: var(--surface) !important;
    color: var(--text-secondary) !important;
    border-color: var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    color: var(--text-primary) !important;
    border-color: var(--border-hover) !important;
    background: #F8FAFC !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border-color: #0F172A !important;
    box-shadow: var(--shadow-sm) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #1E293B !important;
    border-color: #1E293B !important;
}

/* Card Surface */
.panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-sm);
}

.panel-header {
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 12px;
    margin-bottom: 14px;
}

.panel-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 2px;
}

.panel-subtitle {
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin: 0;
}

/* Chat Messages */
.msg-user {
    background: #F1F5F9;
    color: #0F172A;
    padding: 12px 16px;
    border-radius: 12px 12px 2px 12px;
    margin: 10px 0 10px auto;
    max-width: 80%;
    font-size: 0.92rem;
    line-height: 1.5;
    border: 1px solid #E2E8F0;
}

.msg-ai {
    background: var(--surface);
    color: #0F172A;
    padding: 16px 18px;
    border-radius: 12px;
    margin: 10px 0;
    max-width: 90%;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    font-size: 0.92rem;
    line-height: 1.65;
}

.msg-meta {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    background: transparent !important;
}

div[data-testid="stChatInput"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-sm) !important;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 1px #6366F1 !important;
}

/* Native File Uploader Alignment & Fix */
div[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFC !important;
    border: 1px dashed var(--border-hover) !important;
    border-radius: 8px !important;
    padding: 20px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: var(--text-secondary) !important;
}

div[data-testid="stFileUploaderFile"] {
    background: #F1F5F9 !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

/* Slider Track */
div[data-testid="stSlider"] [role="slider"] {
    background-color: #0F172A !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
}

div[data-baseweb="slider"] div[style*="background-color: rgb(255, 75, 75)"],
div[data-baseweb="slider"] div[style*="background: rgb(255, 75, 75)"] {
    background-color: #0F172A !important;
}

/* Metric Display Cards */
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: var(--shadow-sm);
}

.stat-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    font-feature-settings: "tnum";
}

/* Code & Highlights */
p > code, li > code {
    background: #F1F5F9 !important;
    color: #0F172A !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.84rem !important;
    border: 1px solid #E2E8F0 !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(PRODUCTION_CSS, unsafe_allow_html=True)

# ============================================================
# STATE INITIALIZATION
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_summary" not in st.session_state:
    st.session_state.last_summary = None

def navigate(page: str):
    st.session_state.page = page
    st.rerun()

# ============================================================
# TOP APPLICATION BAR
# ============================================================
ai_connected = chat_ai_available()
status_html = (
    '<span class="app-status status-live"><span class="status-dot-live"></span>Azure Cloud Inference</span>'
    if ai_connected
    else '<span class="app-status status-fallback"><span class="status-dot-fallback"></span>Local Edge Fallback</span>'
)

st.markdown(
    f"""
    <div class="app-header">
        <div class="app-brand">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color:#4338CA;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
            LexieLingua
            <span class="app-brand-badge">Workspace</span>
        </div>
        <div>
            {status_html}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Clean Segmented Navigation Tab Controls
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("💬 Conversational Assistant", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary"):
        navigate("chat")
with nav2:
    if st.button("📄 Document Summarizer", use_container_width=True, type="primary" if st.session_state.page == "summarizer" else "secondary"):
        navigate("summarizer")
with nav3:
    if st.button("⚙️ Architecture & Data Flow", use_container_width=True, type="primary" if st.session_state.page == "about" else "secondary"):
        navigate("about")

st.write("")

# ============================================================
# VIEW 1: CONVERSATIONAL ASSISTANT
# ============================================================
if st.session_state.page == "chat":
    left_col, right_col = st.columns([2.7, 1.3])

    with left_col:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">AI Conversational Session</div>
                    <div class="panel-subtitle">Streaming answers for code execution, academic research, and document inquiries.</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.chat_history:
            st.markdown(
                """
                <div style="padding: 16px 0; color: #64748B; font-size: 0.9rem;">
                    Ready for your query. Ask a technical question, paste a function to debug, or select a prompt on the right.
                </div>
                """,
                unsafe_allow_html=True,
            )

        for turn in st.session_state.chat_history:
            is_user = turn["role"] == "user"
            css_class = "msg-user" if is_user else "msg-ai"
            sender_label = "You" if is_user else "LexieLingua Copilot"
            st.markdown(
                f"""
                <div class="{css_class}">
                    <div class="msg-meta">{sender_label}</div>
                    <div>{turn["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        user_input = st.chat_input("Send a message or code snippet...")
        
        if user_input:
            st.markdown(
                f"""
                <div class="msg-user">
                    <div class="msg-meta">You</div>
                    <div>{user_input}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.container():
                st.markdown(
                    """
                    <div class="msg-meta" style="margin: 10px 0 4px 4px; color: #4338CA;">LexieLingua Copilot</div>
                    """,
                    unsafe_allow_html=True,
                )
                stream_gen = stream_answer(user_input, st.session_state.chat_history[:-1])
                full_ai_response = st.write_stream(stream_gen)

            st.session_state.chat_history.append({"role": "assistant", "content": full_ai_response})
            st.rerun()

        if st.session_state.chat_history:
            if st.button("Clear Conversation", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()

    with right_col:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">Suggested Prompts</div>
                    <div class="panel-subtitle">Click to load query into context</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        
        quick_prompts = [
            "Write a Python function to reverse a singly linked list with O(n) time.",
            "Explain quantum computing principles with a concrete computing analogy.",
            "List 4 index optimization strategies for high-write SQL tables.",
            "Draft a 7-day revision schedule for machine learning theory exams.",
        ]
        
        for idx, prompt_text in enumerate(quick_prompts):
            if st.button(prompt_text, key=f"qp_{idx}", type="secondary", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": prompt_text})
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW 2: DOCUMENT SUMMARIZER
# ============================================================
elif st.session_state.page == "summarizer":
    st.markdown(
        """
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">Document Intelligence</div>
                <div class="panel-subtitle">Extract key takeaways and generate executive summaries from multi-page documents.</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    up_col, opt_col = st.columns([2.5, 1])
    with up_col:
        doc_file = st.file_uploader("Upload target document", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
    with opt_col:
        summary_len = st.select_slider("Target length", options=["Short", "Medium", "Long"], value="Medium")
        run_sum = st.button("Generate Summary", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if run_sum:
        if not doc_file:
            st.warning("Please select a file to summarize.")
        else:
            with st.spinner("Processing document..."):
                raw_text = extract_text(doc_file)
                if not raw_text.strip():
                    st.error("Unable to parse text from the uploaded document.")
                else:
                    res = summarize(raw_text, length=summary_len)
                    res["filename"] = doc_file.name
                    res["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state.last_summary = res

    if st.session_state.last_summary:
        sum_data = st.session_state.last_summary
        orig_w = sum_data.get("original_words", 0)
        summ_w = sum_data.get("summary_words", 0)
        reduction = round(100 * (1 - (summ_w / max(orig_w, 1)))) if orig_w else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Source Words</div><div class="stat-value">{orig_w:,}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Summary Words</div><div class="stat-value">{summ_w:,}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Compression</div><div class="stat-value">{reduction}%</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Engine Mode</div><div class="stat-value" style="font-size:1.1rem; padding-top:4px;">{sum_data.get("mode", "Cloud AI")}</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">Executive Summary</div>
                    <div class="panel-subtitle">Synthesized from {sum_data.get('filename')}</div>
                </div>
                <div style="line-height: 1.75; font-size: 0.94rem; color: #334155; white-space: pre-wrap;">
{sum_data.get('summary', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if sum_data.get("key_points"):
            pts = "".join(f"<li style='margin-bottom:8px;'>{p}</li>" for p in sum_data["key_points"])
            st.markdown(
                f"""
                <div class="panel">
                    <div class="panel-header">
                        <div class="panel-title">Key Takeaways</div>
                    </div>
                    <ul style="line-height: 1.7; font-size: 0.92rem; color: #334155; padding-left: 20px; margin: 0;">
                        {pts}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        export_content = f"FILE: {sum_data.get('filename')}\nDATE: {sum_data.get('generated_at')}\n\nSUMMARY:\n{sum_data.get('summary')}\n\nKEY TAKEAWAYS:\n" + "\n".join(f"- {pt}" for pt in sum_data.get("key_points", []))
        st.download_button("Export Report (.txt)", data=export_content, file_name=f"summary_{sum_data.get('filename', 'doc')}.txt", mime="text/plain")

# ============================================================
# VIEW 3: ARCHITECTURE & DATA FLOW
# ============================================================
else:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">System Architecture & Technical Blueprint</div>
                <div class="panel-subtitle">Overview of the processing pipeline, model integration, and data boundaries.</div>
            </div>
            <p style="color: #475569; font-size: 0.9rem; line-height: 1.6; margin: 0;">
                LexieLingua employs a decoupled architecture combining cloud-hosted neural inference with stateless local extraction engines.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)
    steps = [
        ("01", "Ingestion Layer", "Parses raw byte buffers from PDF (PyPDF), DOCX (Python-docx), and plain text."),
        ("02", "Context Pipeline", "Prunes token history and constructs parameterized synthesis prompts."),
        ("03", "Neural Inference", "Executes low-latency completion via Microsoft Azure OpenAI deployments."),
        ("04", "Response Stream", "Yields chunked Server-Sent Events (SSE) directly to the Streamlit UI buffer."),
    ]

    for col, (num, title, desc) in zip([p1, p2, p3, p4], steps):
        with col:
            st.markdown(
                f"""
                <div class="panel" style="min-height: 180px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #4338CA; margin-bottom: 6px;">STEP {num}</div>
                    <div style="font-size: 0.92rem; font-weight: 600; color: #0F172A; margin-bottom: 6px;">{title}</div>
                    <div style="font-size: 0.82rem; color: #64748B; line-height: 1.5;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">Data Privacy & Lifecycle</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 0.88rem; color: #475569; line-height: 1.6;">
                <div>
                    <strong style="color: #0F172A;">Ephemeral Memory Model:</strong> All document uploads and text buffers reside exclusively in session memory (RAM) and are discarded once the active browser session terminates.
                </div>
                <div>
                    <strong style="color: #0F172A;">Zero Storage Persistence:</strong> API payloads sent to the Azure OpenAI endpoint are strictly stateless without secondary data retention or external model training.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
