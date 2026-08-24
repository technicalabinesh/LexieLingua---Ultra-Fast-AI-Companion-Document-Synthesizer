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
    FAQ_KNOWLEDGE_BASE,
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
    page_title="LexieLingua AI | ChatGPT-grade Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# BULLETPROOF SAAS CSS DESIGN SYSTEM
# ============================================================
MODERN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap');

:root {
    --primary: #4F46E5;
    --primary-hover: #4338CA;
    --dark: #0F172A;
    --slate: #475569;
    --border: #E2E8F0;
    --card-bg: #FFFFFF;
    --glass-shadow: 0 10px 30px -4px rgba(79, 70, 229, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
}

/* Global Font & Text */
html, body, p, h1, h2, h3, h4, h5, h6, label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--dark) !important;
}

.stApp {
    background: radial-gradient(circle at 10% 10%, #EDE9FE 0%, transparent 40%),
                radial-gradient(circle at 90% 90%, #E0E7FF 0%, transparent 40%),
                linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%) !important;
}

.main .block-container {
    max-width: 1180px;
    padding: 1.5rem 1.5rem 3.5rem;
}

/* Navbar */
.nav-container {
    background: #FFFFFF !important;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 12px 24px;
    box-shadow: var(--glass-shadow);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-logo {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0F172A !important;
    display: flex;
    align-items: center;
    gap: 6px;
}

.brand-highlight { color: #4F46E5 !important; }

/* Status Badges */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
}

.status-online {
    background: #ECFDF5 !important;
    color: #059669 !important;
    border: 1px solid #A7F3D0;
}

.status-offline {
    background: #FFFBEB !important;
    color: #D97706 !important;
    border: 1px solid #FDE68A;
}

/* Cards */
.ui-card {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px;
    padding: 22px;
    box-shadow: var(--glass-shadow);
    margin-bottom: 18px;
}

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    padding: 10px 18px !important;
    min-height: 44px !important;
    transition: all 0.15s ease-in-out !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #F8FAFC !important;
    border-color: #94A3B8 !important;
    color: #4F46E5 !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: #4F46E5 !important;
    color: #FFFFFF !important;
    border: 1px solid #4338CA !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #4338CA !important;
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35) !important;
}

/* Chat Input */
div[data-testid="stChatInput"] { background: transparent !important; }
div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06) !important;
}
div[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #0F172A !important;
    font-size: 0.96rem !important;
}
div[data-testid="stChatInput"] button {
    background: #4F46E5 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}

/* Chat Message Bubbles */
.chat-user {
    background: #4F46E5 !important;
    color: #FFFFFF !important;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 10px 0 10px auto;
    max-width: 84%;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.18);
    font-size: 0.96rem;
}
.chat-user * { color: #FFFFFF !important; }

.chat-ai {
    background: #FFFFFF !important;
    color: #0F172A !important;
    padding: 18px 22px;
    border-radius: 18px 18px 18px 4px;
    margin: 10px 0;
    max-width: 88%;
    border: 1px solid var(--border);
    box-shadow: var(--glass-shadow);
    font-size: 0.96rem;
    line-height: 1.65;
}

/* Code Blocks */
div[data-testid="stCodeBlock"],
div[data-testid="stCodeBlock"] > div,
pre {
    background-color: #0F172A !important;
    border-radius: 12px !important;
    border: 1px solid #1E293B !important;
    margin: 12px 0 !important;
}

div[data-testid="stCodeBlock"] *,
pre * {
    background-color: transparent !important;
    background: transparent !important;
    font-family: 'Fira Code', 'Cascadia Code', Consolas, monospace !important;
}

div[data-testid="stCodeBlock"] code,
div[data-testid="stCodeBlock"] span,
pre code,
pre span {
    color: #F8FAFC !important;
    font-size: 0.92rem !important;
    line-height: 1.55 !important;
}

/* Inline Code */
p > code, li > code {
    background-color: #EEF2FF !important;
    color: #4F46E5 !important;
    padding: 2px 7px !important;
    border-radius: 6px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border: 1px solid #E0E7FF !important;
}

/* File Uploader */
div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    padding: 16px !important;
    box-shadow: var(--glass-shadow) !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFC !important;
    border: 2px dashed #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 18px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: #1E293B !important;
}

div[data-testid="stFileUploaderDropzone"] button {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}

div[data-testid="stFileUploaderDropzone"] button:hover {
    background: #EEF2FF !important;
    border-color: #4F46E5 !important;
    color: #4F46E5 !important;
}

/* Uploaded file list item */
div[data-testid="stFileUploaderFile"] {
    background: #F1F5F9 !important;
    border-radius: 10px !important;
    border: 1px solid #E2E8F0 !important;
    padding: 10px 14px !important;
    margin-top: 10px !important;
}

div[data-testid="stFileUploaderFile"] * {
    color: #0F172A !important;
    font-weight: 600 !important;
}

div[data-testid="stFileUploaderFile"] svg {
    fill: #4F46E5 !important;
}

/* Slider Track & Indicator */
div[data-testid="stSlider"] [role="slider"] {
    background-color: #4F46E5 !important;
}

div[data-baseweb="slider"] div[style*="background-color: rgb(255, 75, 75)"],
div[data-baseweb="slider"] div[style*="background: rgb(255, 75, 75)"] {
    background-color: #4F46E5 !important;
}

div[data-testid="stSlider"] span {
    color: #4F46E5 !important;
    font-weight: 700 !important;
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
    font-size: 1.7rem;
    font-weight: 800;
    color: #4F46E5 !important;
}
.metric-lbl {
    font-size: 0.75rem;
    color: #64748B !important;
    font-weight: 700;
    text-transform: uppercase;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(MODERN_CSS, unsafe_allow_html=True)

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
# TOP BRANDING & NAVIGATION
# ============================================================
ai_connected = chat_ai_available()
status_html = (
    '<span class="status-pill status-online">⚡ Ultra-Fast Streaming Active</span>'
    if ai_connected
    else '<span class="status-pill status-offline">● Offline Fallback</span>'
)

st.markdown(
    f"""
    <div class="nav-container">
        <div class="brand-logo">
            ✦ Lexie<span class="brand-highlight">Lingua</span> AI
        </div>
        <div>
            {status_html}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button("💬 AI Assistant", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary"):
        navigate("chat")
with nav_cols[1]:
    if st.button("📄 Document Summarizer", use_container_width=True, type="primary" if st.session_state.page == "summarizer" else "secondary"):
        navigate("summarizer")
with nav_cols[2]:
    if st.button("ℹ Architecture", use_container_width=True, type="primary" if st.session_state.page == "about" else "secondary"):
        navigate("about")

st.write("")

# ============================================================
# CHAT VIEW (REAL-TIME STREAMING)
# ============================================================
if st.session_state.page == "chat":
    left_col, right_col = st.columns([2.5, 1])

    with left_col:
        st.markdown(
            """
            <div class="ui-card" style="margin-bottom:12px; padding:18px 22px;">
                <h3 style="margin:0 0 2px; font-weight:800; font-size:1.3rem;">💬 AI Conversational Copilot</h3>
                <p style="color:#64748B; font-size:0.9rem; margin:0;">Real-time AI for coding, deep problem solving, academic reasoning, and study prep.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Message Display
        if not st.session_state.chat_history:
            st.markdown(
                """
                <div class="chat-ai">
                    👋 <b>Hello! I am your AI Copilot.</b><br>
                    Ask me anything — write code, solve math, explain complex ideas, or brainstorm essays.
                </div>
                """,
                unsafe_allow_html=True,
            )

        for turn in st.session_state.chat_history:
            css_class = "chat-user" if turn["role"] == "user" else "chat-ai"
            sender = "👤 You" if turn["role"] == "user" else "✦ LexieLingua"
            st.markdown(
                f"""
                <div class="{css_class}">
                    <div style="font-size:0.74rem; opacity:0.85; margin-bottom:4px; font-weight:700;">{sender}</div>
                    <div>{turn["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Streaming Chat Input
        user_input = st.chat_input("Ask any question (e.g. Write a Python script to reverse a linked list)...")
        
        if user_input:
            # Display user bubble immediately
            st.markdown(
                f"""
                <div class="chat-user">
                    <div style="font-size:0.74rem; opacity:0.85; margin-bottom:4px; font-weight:700;">👤 You</div>
                    <div>{user_input}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Stream Assistant Tokens in Real-Time
            with st.container():
                st.markdown(
                    """
                    <div style="font-size:0.74rem; color:#4F46E5; margin:10px 0 2px; font-weight:800;">✦ LexieLingua</div>
                    """,
                    unsafe_allow_html=True,
                )
                stream_gen = stream_answer(user_input, st.session_state.chat_history[:-1])
                full_ai_response = st.write_stream(stream_gen)

            st.session_state.chat_history.append({"role": "assistant", "content": full_ai_response})
            st.rerun()

        if st.session_state.chat_history:
            st.write("")
            if st.button("🗑 Reset Conversation", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    with right_col:
        st.markdown(
            """
            <div class="ui-card">
                <h4 style="margin:0 0 12px; font-weight:700; font-size:1rem;">⚡ Try Asking</h4>
            """,
            unsafe_allow_html=True,
        )
        prompts = [
            "Write a Python script to reverse a linked list.",
            "Explain quantum computing in simple terms.",
            "How do I optimize SQL queries for large datasets?",
            "Give me 5 study strategies for difficult exams.",
        ]
        for idx, prompt_text in enumerate(prompts):
            if st.button(prompt_text, key=f"quick_{idx}", type="secondary", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": prompt_text})
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SUMMARIZER VIEW
# ============================================================
elif st.session_state.page == "summarizer":
    st.markdown(
        """
        <div class="ui-card" style="margin-bottom:18px;">
            <h3 style="margin:0 0 4px; font-weight:800;">📄 Intelligent Document Summarizer</h3>
            <p style="color:#64748B; font-size:0.9rem; margin:0;">Upload lecture notes, papers, or code files for structured summaries and key points.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    up_col, opt_col = st.columns([2, 1])
    with up_col:
        doc_file = st.file_uploader("Upload document", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")
    with opt_col:
        summary_len = st.select_slider("Length requirement", options=["Short", "Medium", "Long"], value="Medium")
        run_sum = st.button("✨ Generate Summary", type="primary", use_container_width=True)

    if run_sum:
        if not doc_file:
            st.warning("Please upload a document first.")
        else:
            with st.spinner("Extracting text and synthesizing points..."):
                raw_text = extract_text(doc_file)
                if not raw_text.strip():
                    st.error("No readable text found in document.")
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

        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{orig_w}</div><div class="metric-lbl">Original Words</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{summ_w}</div><div class="metric-lbl">Summary Words</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{reduction}%</div><div class="metric-lbl">Compression</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.1rem; margin-top:6px;">{sum_data.get("mode", "AI")}</div><div class="metric-lbl">Mode</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown(
            f"""
            <div class="ui-card">
                <h4 style="margin:0 0 10px; font-weight:700;">📝 Executive Summary</h4>
                <p style="line-height:1.75; font-size:1rem; color:#1E293B; white-space:pre-wrap; margin:0;">{sum_data.get('summary', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if sum_data.get("key_points"):
            pts = "".join(f"<li style='margin-bottom:8px;'>{p}</li>" for p in sum_data["key_points"])
            st.markdown(
                f"""
                <div class="ui-card">
                    <h4 style="margin:0 0 10px; font-weight:700;">🔑 Key Takeaways</h4>
                    <ul style="line-height:1.7; font-size:0.95rem; color:#334155; padding-left:20px; margin:0;">{pts}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        export_content = f"SUMMARY: {sum_data.get('filename')}\nGenerated: {sum_data.get('generated_at')}\n\n{sum_data.get('summary')}\n\nKEY TAKEAWAYS:\n" + "\n".join(f"- {pt}" for pt in sum_data.get("key_points", []))
        st.download_button("⬇ Download Export (.txt)", data=export_content, file_name=f"summary_{sum_data.get('filename', 'doc')}.txt", mime="text/plain", use_container_width=True)

# ============================================================
# ARCHITECTURE & HOW IT WORKS VIEW
# ============================================================
else:
    st.markdown(
        """
        <div class="ui-card" style="margin-bottom:20px; padding:32px;">
            <div class="status-pill status-online" style="margin-bottom:12px;">✦ SYSTEM BLUEPRINT & DATA FLOW</div>
            <h2 style="margin:0 0 8px; font-weight:800; font-size:1.8rem;">How LexieLingua Works</h2>
            <p style="color:#64748B; font-size:1.02rem; margin:0; line-height:1.6;">
                LexieLingua is built on a dual-engine architecture combining enterprise Azure OpenAI cloud intelligence 
                with local edge parsing for zero-downtime reliability.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Pipeline Flow Cards
    st.markdown("### 🔄 End-to-End Processing Pipeline")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown(
            """
            <div class="ui-card" style="min-height:220px; border-top:4px solid #4F46E5;">
                <div style="font-size:1.4rem; margin-bottom:8px;">1️⃣ Ingestion</div>
                <h4 style="margin:0 0 6px; font-size:1rem; font-weight:700;">Input Stream</h4>
                <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
                    Captures conversational chat prompts or extracts raw text from PDF, DOCX, TXT, and Markdown files.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            """
            <div class="ui-card" style="min-height:220px; border-top:4px solid #7C3AED;">
                <div style="font-size:1.4rem; margin-bottom:8px;">2️⃣ Context Layer</div>
                <h4 style="margin:0 0 6px; font-size:1rem; font-weight:700;">Prompt Engine</h4>
                <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
                    Structures conversation history (last 8 turns) and formats synthesis instructions without hallucination.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p3:
        st.markdown(
            """
            <div class="ui-card" style="min-height:220px; border-top:4px solid #059669;">
                <div style="font-size:1.4rem; margin-bottom:8px;">3️⃣ Neural Inference</div>
                <h4 style="margin:0 0 6px; font-size:1rem; font-weight:700;">Azure GPT-5.4</h4>
                <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
                    Processes input via high-throughput global standard deployment on Microsoft Azure Foundry.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p4:
        st.markdown(
            """
            <div class="ui-card" style="min-height:220px; border-top:4px solid #D97706;">
                <div style="font-size:1.4rem; margin-bottom:8px;">4️⃣ Streaming Output</div>
                <h4 style="margin:0 0 6px; font-size:1rem; font-weight:700;">SSE Response</h4>
                <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
                    Streams tokens word-by-word with &lt;250ms TTFT, or formats structured executive summaries.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 2. Detailed Technical Breakdown
    col_tech1, col_tech2 = st.columns(2)

    with col_tech1:
        st.markdown(
            """
            <div class="ui-card">
                <h3 style="font-weight:800; font-size:1.25rem; margin-bottom:12px;">💬 Real-Time Conversational AI</h3>
                <ul style="color:#334155; line-height:1.8; font-size:0.92rem; padding-left:18px;">
                    <li><b>Server-Sent Events (SSE) Streaming:</b> Tokens are yielded to the UI in real time using generator pipelines rather than blocking HTTP responses.</li>
                    <li><b>Persistent TCP Connection Pooling:</b> Reuses an active singleton client to eliminate 150ms–300ms TLS handshake overhead per turn.</li>
                    <li><b>Sliding Context Window:</b> Dynamically retains recent conversation turns while pruning older messages to maintain low latency.</li>
                    <li><b>Multi-Domain Expertise:</b> Answers coding, mathematical derivation, essay structuring, and general academic topics seamlessly.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_tech2:
        st.markdown(
            """
            <div class="ui-card">
                <h3 style="font-weight:800; font-size:1.25rem; margin-bottom:12px;">📄 Intelligent Document Engine</h3>
                <ul style="color:#334155; line-height:1.8; font-size:0.92rem; padding-left:18px;">
                    <li><b>Multi-Format File Parsing:</b> Direct byte extraction from <code>.pdf</code> (via PyPDF), <code>.docx</code> (via Python-docx), and plain text/markdown.</li>
                    <li><b>Configurable Length Synthesis:</b> User-adjustable parameters (Short, Medium, Long) modifying prompt compression targets.</li>
                    <li><b>Key-Takeaway Distillation:</b> Extracts exactly 5 critical bullet points alongside an executive overview.</li>
                    <li><b>Offline Statistical Fallback:</b> Uses term-frequency sentence scoring if cloud connection is unavailable.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 3. System Specs
    st.markdown("### ⚙️ System Specifications & Technology Stack")
    
    spec_col1, spec_col2, spec_col3, spec_col4 = st.columns(4)
    with spec_col1:
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-val" style="font-size:1.3rem;">Azure GPT-5.4</div>
                <div class="metric-lbl">LLM Engine</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with spec_col2:
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-val" style="font-size:1.3rem;">&lt; 250 ms</div>
                <div class="metric-lbl">Time to First Token</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with spec_col3:
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-val" style="font-size:1.3rem;">Streamlit + Python</div>
                <div class="metric-lbl">Frontend & Logic</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with spec_col4:
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-val" style="font-size:1.3rem;">Zero-Persistence</div>
                <div class="metric-lbl">Privacy & Security</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(
        """
        <div class="ui-card" style="background:#F8FAFC !important; border:1px dashed #CBD5E1 !important;">
            <h4 style="margin:0 0 6px; font-weight:700;">🔐 Security & Data Privacy Architecture</h4>
            <p style="color:#475569; font-size:0.9rem; margin:0; line-height:1.6;">
                All credentials (API keys, endpoints, and deployment names) are strictly isolated in environment variables. 
                Uploaded documents are processed in memory and never written to permanent disk storage or shared across sessions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )