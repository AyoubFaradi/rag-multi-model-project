from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from rag_core import answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/rag-chat")
async def rag_chat(request: Request):
    body = await request.json()
    question = body.get("question", "")

    # 🔥 VRAI RAG (PDF + pgvector)
    resp_text, _ = answer(question, k=5)

    return {"answer": resp_text}