import os
import glob
from tqdm import tqdm
from pypdf import PdfReader
from db import get_conn
from openai_utils import embed_text, caption_image

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def chunk_text(text: str) -> list[str]:
    """Découpe un texte en chunks chevauchants."""
    chunks: list[str] = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + CHUNK_SIZE])
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def ingest_pdf(path: str) -> list[str]:
    """Extrait le texte d'un PDF et le découpe en chunks."""
    reader = PdfReader(path)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return chunk_text(full_text)


def ingest_images(paths: list[str]) -> list[tuple[str, str]]:
    """Génère une caption pour chaque image (via OpenAI) et retourne (path, caption)."""
    image_chunks: list[tuple[str, str]] = []
    for p in paths:
        cap = caption_image(p)
        image_chunks.append((p, cap))
    return image_chunks


def save_chunk(conn, source: str, chunk: str, modality: str, emb):
    """Insère un chunk et son embedding dans la table documents."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents(source, chunk, modality, embedding)
            VALUES (%s, %s, %s, %s)
            """,
            (source, chunk, modality, emb),
        )
    conn.commit()


def main(data_dir: str = "data"):
    conn = get_conn()

    pdfs = glob.glob(os.path.join(data_dir, "*.pdf"))
    imgs = glob.glob(os.path.join(data_dir, "*.png")) + glob.glob(os.path.join(data_dir, "*.jpg"))

    # PDFs -> texte
    if pdfs:
        for pdf in tqdm(pdfs, desc="PDF ingestion"):
            for c in ingest_pdf(pdf):
                emb = embed_text(c)
                save_chunk(conn, pdf, c, "text", emb)
    else:
        print("Aucun PDF trouvé dans", data_dir)

    # Images -> caption -> embedding
    if imgs:
        for img_path, cap in tqdm(ingest_images(imgs), desc="Image ingestion"):
            emb = embed_text(cap)
            save_chunk(conn, img_path, cap, "image", emb)
    else:
        print("Aucune image trouvée dans", data_dir)

    print("Ingestion terminée")


if __name__ == "__main__":
    main()