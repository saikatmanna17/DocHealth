from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from litellm import completion
from app.llm_provider import get_llm
from app.rag_service import retrieve

router = APIRouter()

def build_prompt(context, query):
    return f"""
Use ONLY the context below.

Context:
{context}

Question:
{query}

Rules:
- No hallucination
- If not found say EXACTLY: Not found in document
"""

@router.get("/ask")
def ask(query: str):
    docs = retrieve(query)

    if not docs:
        return {"answer": "No relevant data found", "sources": [], "confidence": 0}

    context = "\n\n".join([d.page_content for d in docs])[:4000]
    model = get_llm()

    response = completion(
        model=f"groq/{model}",
        messages=[
            {"role": "user", "content": build_prompt(context, query)}
        ],
        stream=False
    )

    answer = response["choices"][0]["message"]["content"]

    return {
        "answer": answer,
        "sources": [d.page_content[:200] for d in docs],
        "confidence": round(min(len(docs) / 5, 1.0), 2)
    }

@router.get("/ask-stream")
def ask_stream(query: str):

    docs = retrieve(query)
    context = "\n\n".join([d.page_content for d in docs])[:4000]
    model = get_llm()

    def generate():
        response = completion(
            model=f"groq/{model}",
            messages=[
                {"role": "user", "content": build_prompt(context, query)}
            ],
            stream=True
        )

        for chunk in response:
            if "choices" in chunk:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]

    return StreamingResponse(generate(), media_type="text/plain")

def answer_query(query: str):
    from app.rag_service import retrieve
    from litellm import completion
    from app.llm_provider import get_llm

    docs = retrieve(query)
    context = "\n\n".join([d.page_content for d in docs])[:4000]

    model = get_llm()

    response = completion(
        model=f"groq/{model}",
        messages=[
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
        ]
    )

    return response["choices"][0]["message"]["content"]