CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    source TEXT,
    chunk TEXT,
    modality TEXT,
    embedding VECTOR(1536)
);
