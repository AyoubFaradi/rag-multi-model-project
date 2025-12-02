from db import get_conn
from openai_utils import embed_text
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def retrieve(query: str, k=5):
    q_emb = embed_text(query)
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT source, chunk, modality,
                   1 - (embedding <=> %s::vector) AS score
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (q_emb, q_emb, k)
        )
        return cur.fetchall()


def answer(query: str, k=5):
    rows = retrieve(query, k=k)

    # rows = [(source, chunk, modality, score), ...]
    context = "\n\n".join([f"[{m}] {c}" for _, c, m, _ in rows])

    prompt = f"""
Tu es un assistant RAG multimodal.
Réponds UNIQUEMENT en utilisant le contexte ci-dessous.
Si l'information n’est pas dans le contexte, dis-le.

Contexte :
{context}

Question :
{query}

Réponse :
"""

    resp = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return resp.output_text, rows
