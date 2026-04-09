# 🚀 AnalyzeReportCrewAI

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.101-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-v1.27-orange.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**AnalyzeReportCrewAI** is a **full-stack AI SaaS platform** for **document ingestion, retrieval, and summarization**.  
It leverages **Groq LLM**, **FAISS vector database**, and a **Streamlit UI** with **streaming answers and source highlighting**.

---

## 🔹 Features

- Secure **login system** with JWT authentication  
- Upload **PDF and text files** for analysis  
- **RAG pipeline**: document chunking → embeddings → FAISS vector store  
- Powered by **Groq LLM** (lightweight, fast, no Hugging Face memory overhead)  
- **Streaming responses** for real-time AI answers  
- **Source highlighting** for transparency  
- Confidence scores for answers  
- **Streamlit UI** for interactive user experience  
- Multi-user ready architecture  

---

## 🔹 Project Structure
project/
│
├── app/
│ ├── main.py # FastAPI backend
│ ├── config.py # Environment & settings
│ ├── llm_provider.py # Auto-detect Groq model
│ ├── rag_service.py # RAG pipeline (chunk/embed/retrieve)
│ ├── auth.py # JWT login
│
├── uploads/ # Uploaded files storage
├── vectorstore/ # FAISS embeddings storage
├── streamlit_app.py # Streamlit UI
└── .env # API keys & paths


---

## 🔹 Requirements

- Python 3.11+  
- Install dependencies:

```bash
uv pip install "crewai[litellm]" litellm groq fastapi uvicorn streamlit \
langchain langchain-community langchain-huggingface faiss-cpu \
sentence-transformers python-jose passlib bcrypt


## How to Run in Terminal 1
uvicorn app:app --reload

## How to Run in Terminal 2
streamlit run streamlit_app.py

## Credentials to login
Username: admin
Password: admin

## Workflow
Login using the admin credentials
Upload a PDF or text file
Ask a question about the document
Receive streaming AI answers with highlighted sources

## Architecture Overview

Workflow:

User uploads document →
Document is chunked & embedded →
Stored in FAISS vector database →
User asks a query →
Top chunks are retrieved →
Groq LLM generates streaming answer →
UI shows answer with source highlighting