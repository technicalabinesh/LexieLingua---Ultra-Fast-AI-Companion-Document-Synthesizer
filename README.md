# LexieLingua AI  
### *AI-Powered Student Support Chatbot & Intelligent Document Summarizer*

LexieLingua AI is a modern academic productivity web app that combines conversational AI assistance and document summarization in a single Streamlit experience.

<img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg">
<img src="https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg">
<img src="https://img.shields.io/badge/Azure%20OpenAI-GPT--5.4-0078D4.svg">
<img src="https://img.shields.io/badge/License-MIT-green.svg">

---

## 1) Project Overview

LexieLingua AI is built for students, researchers, and learners who need:
- an AI-powered academic assistant for real-time Q&A, coding help, and study guidance, and
- an intelligent summarization engine for PDFs, DOCX, TXT, and Markdown documents.

It uses **Azure OpenAI GPT-5.4** for AI responses and includes an **offline local extractive fallback** for summarization when cloud AI is unavailable.

---

## 2) Why LexieLingua AI?

- Combines two high-value student workflows in one app: **chat + summarization**
- Supports **multi-format document upload**
- Provides **key takeaways + compression metrics**
- Designed with a **modern, recruiter-friendly Streamlit UI**
- Includes a **resilience path** via local extractive summarization fallback

---

## 3) Key Features

### AI Student Support Chatbot
- Azure OpenAI GPT-5.4
- Real-time token streaming
- Academic question answering
- Programming and coding assistance
- Mathematical and logical problem solving
- Essay and content assistance
- General student support
- Conversation history using Streamlit session state

### Intelligent Document Summarizer
- Upload PDF, DOCX, TXT, and MD files
- Extract text from uploaded documents
- Generate AI-powered summaries
- Generate key takeaways
- Display original word count
- Display summary word count
- Calculate compression/reduction percentage
- Useful for lecture notes, research papers, assignments, and study materials

### Offline Fallback
- If Azure OpenAI is unavailable or credentials are missing, summarization falls back to a **lightweight frequency-based extractive summarization engine**
- Produces summary + key takeaways without cloud inference

### User Interface
- Modern Streamlit interface
- Glassmorphism-inspired design
- Responsive layout
- Custom CSS
- Clean navigation
- Code formatting for technical answers
- Academic SaaS-style appearance

---

## 4) Demo

**[Add application screenshot here]**

---

## 5) System Architecture

```text
User
  ↓
Streamlit Web Application
  ↓
 ┌──────────────────────────────┐
 │                              │
 ↓                              ↓
AI Chatbot                 Document Engine
 │                              │
 ↓                              ↓
Azure OpenAI              PDF/DOCX/TXT/MD
 │                              │
 ↓                              ↓
GPT-5.4                    Text Extraction
 │                              │
 └──────────────┬───────────────┘
                ↓
          Results / UI
                ↓
       Student / Researcher
```

### Offline Fallback Path

```text
Azure OpenAI unavailable
        ↓
Local Extractive Summarization
        ↓
Summary + Key Takeaways
```

---

## 6) Application Workflow

1. User opens the Streamlit app.
2. User chooses either:
   - **AI Assistant**, or
   - **Document Summarizer**.
3. Chat requests are sent to Azure OpenAI for generated responses with streamed output.
4. Uploaded files are parsed (PDF/DOCX/TXT/MD), then summarized.
5. If Azure OpenAI is unavailable for summarization, local extractive fallback is used.
6. UI displays results, key takeaways, and word-count/compression metrics.

---

## 7) Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.10+ |
| UI Framework | Streamlit 1.35+ |
| LLM Provider | Azure OpenAI |
| Model | GPT-5.4 |
| SDK | OpenAI Python SDK |
| Document Parsing | PyPDF, python-docx |
| Config Management | python-dotenv |
| NLP Helpers | Lightweight local frequency-based extractive logic |

---

## 8) Project Structure

```text
lexielingua-ai/
│
├── app.py
├── chatbot.py
├── summarizer.py
├── utils.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

### File Descriptions

- `app.py` → Main Streamlit application and UI  
- `chatbot.py` → Azure OpenAI chatbot and streaming response logic  
- `summarizer.py` → Document summarization logic  
- `utils.py` → Document text extraction and helper/NLP functions  
- `requirements.txt` → Python dependencies  
- `.env.example` → Environment variable template  
- `.gitignore` → Prevent secrets and unnecessary files from being committed  

---

## 9) Prerequisites

- Python 3.10 or higher
- pip
- Azure OpenAI resource and deployment (`gpt-5.4`)
- Git

---

## 10) Installation

### Windows (PowerShell)

```powershell
git clone https://github.com/YOUR_USERNAME/lexielingua-ai.git
cd lexielingua-ai

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

### macOS/Linux

```bash
git clone https://github.com/YOUR_USERNAME/lexielingua-ai.git
cd lexielingua-ai

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## 11) Virtual Environment Setup

If not already activated:

- **Windows PowerShell**
  ```powershell
  venv\Scripts\activate
  ```

- **macOS/Linux**
  ```bash
  source venv/bin/activate
  ```

---

## 12) Install Requirements

```bash
pip install -r requirements.txt
```

---

## 13) Environment Variable Configuration

Create a `.env` file in the project root:

```env
AZURE_OPENAI_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com/"
AZURE_OPENAI_API_KEY="your_azure_api_key_here"
AZURE_OPENAI_DEPLOYMENT="gpt-5.4"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
```

---

## 14) Running Locally

```bash
streamlit run app.py
```

---

## 15) Azure OpenAI Setup

1. Create an Azure OpenAI resource in Azure.
2. Deploy model: `gpt-5.4`.
3. Copy:
   - Endpoint URL
   - API key
   - Deployment name
4. Add values to `.env`.
5. Run the Streamlit app.

> This project is configured for the **Azure OpenAI Responses API style** with `input=...` request content patterns (not legacy `messages=[...]` Chat Completions format in documentation).

---

## 16) Streamlit Cloud Deployment

1. Push project to GitHub.
2. Ensure `.env` is included in `.gitignore`.
3. Create a new Streamlit Cloud app.
4. Select your GitHub repository.
5. Select `app.py` as the entry point.
6. Add secrets in Streamlit Cloud Secrets.

---

## 17) Streamlit Secrets Configuration

Add the following to Streamlit Secrets (TOML):

```toml
AZURE_OPENAI_ENDPOINT = "https://your-resource-name.cognitiveservices.azure.com/"
AZURE_OPENAI_API_KEY = "your_azure_api_key_here"
AZURE_OPENAI_DEPLOYMENT = "gpt-5.4"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
```

---

## 18) Security and Privacy

- Never hardcode API keys in source code.
- Never commit `.env` to GitHub.
- Never expose Azure OpenAI API keys in logs, screenshots, or commits.
- Use Streamlit Secrets for cloud deployment credentials.
- Uploaded documents should be processed in memory where supported by the implementation.
- Avoid printing confidential document contents to logs.

---

## 19) Offline Fallback Behavior

When Azure OpenAI is unavailable or credentials are missing:
- The app uses a **local frequency-based extractive summarization** fallback.
- It still returns:
  - summary
  - key takeaways
  - word count metrics

This improves reliability for student workflows during connectivity or configuration issues.

---

## 20) Example Use Cases

- Summarizing lecture notes before exams
- Extracting key points from research papers
- Quick assignment brief digestion
- Asking coding questions while studying
- Converting long notes into concise revision material

---

## 21) Future Enhancements

- Multi-document batch summarization
- Export to PDF/Markdown formats
- Topic-wise summary segmentation
- Citation-aware summarization pipeline
- User authentication and personalized history

---

## 22) Limitations

- AI output quality depends on model behavior and prompt quality.
- Very large or poorly formatted documents may affect extraction quality.
- Cloud features require valid Azure OpenAI credentials and quota.
- Local fallback is extractive and may be less semantically rich than cloud generative summaries.

---

## 23) Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 24) License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for details.

---

## 👨‍💻 Author

Abinesh M.  
B.Tech Artificial Intelligence & Data Science  

GitHub: https://github.com/technicalabinesh
