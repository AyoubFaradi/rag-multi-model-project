from db import get_conn
from openai_utils import embed_text
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def retrieve(query: str, k: int = 5):
    """
    Recherche top-k par similarité dans la table documents.
    Retourne une liste de tuples : (source, chunk, modality, score)
    """
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
            (q_emb, q_emb, k),
        )
        rows = cur.fetchall()
    conn.close()
    return rows


def answer(query: str, k: int = 5):
    """
    Construit le contexte à partir des chunks récupérés et appelle le modèle.
    Retourne la réponse du modèle et les rows (contexte) pour inspection.
    """
    rows = retrieve(query, k=k)

    # rows : list of (source, chunk, modality, score)
    context = "\n\n".join([f"[{modality}] {chunk}" for source, chunk, modality, score in rows])

    prompt = f"""
Tu es un assistant RAG multimodal.
Utilise STRICTEMENT le contexte pour répondre.
Contexte:
{context}
Question:
{query}
Réponse:
"""

    resp = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    return resp.output_text, rows