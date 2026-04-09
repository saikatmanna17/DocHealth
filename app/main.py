# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import os

from pydantic import BaseModel
from litellm import completion

from app.auth import create_token
from app.config import settings
from app.rag_service import process_document, retrieve
from app.llm_provider import get_llm

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------- LOGIN --------
class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest):
    if data.username.strip() == "admin" and data.password.strip() == "admin":
        return {"token": create_token(data.username)}

    raise HTTPException(status_code=401, detail="Invalid credentials")


# -------- UPLOAD --------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        path = os.path.join(UPLOAD_DIR, file.filename)

        with open(path, "wb") as f:
            f.write(await file.read())

        process_document(path)

        return {"message": "Uploaded & processed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- ASK --------
@app.get("/ask")
def ask(query: str):
    docs = retrieve(query)

    if not docs:
        return {"answer": "Upload a document first", "sources": [], "confidence": 0}

    context = "\n\n".join([d.page_content for d in docs])[:4000]

    model = get_llm()

    response = completion(
        model=f"groq/{model}",
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{query}"
            }
        ]
    )

    answer = response["choices"][0]["message"]["content"]

    return {
        "answer": answer,
        "sources": [d.page_content[:200] for d in docs],
        "confidence": min(1.0, len(docs) / 5)
    }


# -------- STREAM --------
@app.get("/ask-stream")
def ask_stream(query: str):

    def generate():
        docs = retrieve(query)

        if not docs:
            yield "Upload document first"
            return

        context = "\n\n".join([d.page_content for d in docs])[:4000]
        model = get_llm()

        response = completion(
            model=f"groq/{model}",
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion:\n{query}"
                }
            ],
            stream=True
        )

        for chunk in response:
            if chunk and "choices" in chunk:
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content

    return StreamingResponse(generate(), media_type="text/plain")

