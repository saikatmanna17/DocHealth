# rag_service.py

import os
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from app.config import settings

# ---------- GLOBAL EMBEDDINGS (LOAD ONCE) ----------
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings


# ---------- LOAD DOCUMENT ----------
def load_documents(file_path: str) -> List[Document]:
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")

    docs = loader.load()

    # Add metadata (page/source)
    for d in docs:
        d.metadata["source"] = file_path

    return docs


# ---------- SPLIT ----------
def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)


# ---------- INDEX ----------
def index_documents(chunks: List[Document]):
    embeddings = get_embeddings()

    if os.path.exists(settings.VECTOR_PATH):
        db = FAISS.load_local(
            settings.VECTOR_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        db.add_documents(chunks)
    else:
        db = FAISS.from_documents(chunks, embeddings)

    db.save_local(settings.VECTOR_PATH)


# ---------- PROCESS (USED IN /upload) ----------
def process_document(file_path: str):
    docs = load_documents(file_path)
    chunks = split_documents(docs)
    index_documents(chunks)


# ---------- RETRIEVE ----------
def retrieve(query: str, k: int = 4) -> List[Document]:
    embeddings = get_embeddings()

    # Handle empty DB case
    if not os.path.exists(settings.VECTOR_PATH):
        return []

    db = FAISS.load_local(
        settings.VECTOR_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = db.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)