# RAG Multimodal — Projet (Rapport)

> Résumé du projet

Ce projet implémente un pipeline RAG (Retrieval Augmented Generation) multimodal :
- Indexation et recherche vectorielle (texte + images) via PostgreSQL + extension pgvector
- Embeddings et génération de texte via l'API OpenAI (embeddings `text-embedding-3-small` et modèle LLM `gpt-5`)
- Interface REST et UI Streamlit pour interroger l'index et obtenir des réponses basées uniquement sur le contexte indexé

---

##  Objectif

Construire un assistant RAG multimodal capable de :
- Ingest (fichiers PDF / images) : convertir en textes / captions puis créer des embeddings
- Stocker embeddings dans Postgres + pgvector
- Effectuer une recherche par similarité (k-NN) pour récupérer un contexte pertinent
- Interroger un LLM (OpenAI) en fournissant le contexte pour obtenir une réponse basée sur ce contexte

---

##  Structure du projet

- `api.py` — microservice Flask exposant l'endpoint `/ask` (POST) qui retourne la réponse et le contexte.
- `app.py` — interface Streamlit (UI) pour poser une question et afficher la réponse + contexte.
- `ingest.py` — script d'ingestion: lit les PDFs et images depuis `data/`, segmente, génère des embeddings, et enregistre en DB.
- `rag_core.py` — logique principale : retrieve (pgvector query) et envoyer le prompt au modèle OpenAI.
- `openai_utils.py` — fonctions utilitaires pour embeddings, captioning d'images, etc.
- `db.py` — gestion de la connexion à la base de données (Postgres + pgvector)
- `db.sql` — SQL pour créer la table `documents` et activer l'extension `vector`.
- `docker-compose.yaml` — service Postgres avec pgvector (image `pgvector/pgvector:pg16`).
- `data/` — dossier destiné à contenir PDFs et images à ingérer.
- `requirements.txt` — dépendances Python.

---

##  Prérequis

- Docker & Docker Compose (pour Postgres + pgvector)
- Python 3.10+ (le projet montre des artefacts Python 3.11)
- Un compte OpenAI et une clé API valide (ne pas publier publiquement)
- (Facultatif) psql / psycopg2 installé localement

---

##  Variables d'environnement (exemple `.env`)

Ne stockez jamais vos clés en clair dans un repo public. Placez-les dans un fichier `.env` ou un gestionnaire de secrets.

Exemple de `.env` :

```
OPENAI_API_KEY=sk-...  # NE PAS COMMIT
PG_HOST=localhost
PG_PORT=5432
PG_DB=ragdb
PG_USER=raguser
PG_PASSWORD=ragpass
```

---

## Installation (Windows - cmd.exe)

1. Créer et activer un environnement virtuel:

```cmd
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Démarrer la base Postgres+pgvector avec Docker Compose:

```cmd
docker-compose up -d
```

3. Initialiser la base de données (exécuter `db.sql`) :

Option A — si psql est accessible localement :

```cmd
psql -h localhost -U raguser -d ragdb -f db.sql
```

Option B — via docker exec (Windows `type` permet d'envoyer un fichier à la commande) :

```cmd
type db.sql | docker exec -i pgvector_rag psql -U raguser -d ragdb
```

Note : sur d'autres OS, remplacez `type` par `cat`.

---

## Ingestion des données

1. Placez vos PDFs (`*.pdf`) et images (`*.png`, `*.jpg`) dans le répertoire `data/`.
2. Lancer l'ingestion :

```cmd
python ingest.py
```

- `ingest.py` segmente les textes (CHUNK_SIZE / CHUNK_OVERLAP) et génère des embeddings pour chaque chunk.
- Les images sont converties en captions (via l'API OpenAI) puis encodées pour embeddings.

---

## Lancer l'API

Démarrer le service Flask (expose `/ask`) :

```cmd
python api.py
```

Exemple de requête via `curl` (Windows - PowerShell):

```powershell
curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d "{\"question\": \"Qu'est-ce que le projet fait ?\"}" | jq
```

Réponse JSON :

```
{
  "answer": "...",
  "context": [ {"source": "file.pdf", "modality": "text", "chunk": "...", "score": 0.97 }, ...]
}
```

---

## Lancer l'UI Streamlit

```cmd
streamlit run app.py
```

Ouvrir le navigateur grâce à l'URL fournie par Streamlit (généralement `http://localhost:8501`).

---

## Détails techniques

- Embeddings : `text-embedding-3-small` (OpenAI). Taille d'embedding = 1536 (table `embedding VECTOR(1536)`).
- Recherche : `ORDER BY embedding <=> %s::vector` (distance cos / inner-product selon la config de pgvector).
- LLM : `gpt-5` (via `client.responses.create`), un prompt construit en s'assurant explicitement que la réponse doit se baser uniquement sur le contexte.

---

## Exemple d'utilisation (flow)

1. Démarrer le conteneur Postgres + pgvector
2. Initialiser la DB (`db.sql`)
3. Placer des documents dans `data/` et exécuter `python ingest.py`
4. Lancer `python api.py` ou `streamlit run app.py`
5. Poser des questions via l'UI ou l'endpoint `/ask`.

---

## Sécurité & Nettoyage

- Ne poussez jamais la clé `OPENAI_API_KEY` dans le repo.
- Pour la production, utilisez des secrets manager (AWS, Azure, GCP, Hashicorp Vault).
- Nettoyez la DB si nécessaire :

```sql
DELETE FROM documents;
```

---

## Extensions / Améliorations possibles

- Ajouter une pagination et métadonnées sur les documents (title, author, page)
- Supporter davantage de formats (DOCX, HTML) et extensible pour captions multi-modal
- Evaluation automatique des réponses (QA dataset) et tests de robustesse
- Authentification / quotas pour l'API
- Index et recherche côté client + visualisation de similarité

---

## Authors & Contributions

- Auteur principal: Ayoub Faradi (présent dans l'arborescence)
- Contributions: PR, issues, suggestions sont les bienvenues

---
