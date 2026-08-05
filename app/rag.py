from functools import lru_cache

import cohere
from groq import Groq
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import (
    CHUNK_OVERLAP_CHARS,
    CHUNK_SIZE_CHARS,
    COHERE_API_KEY,
    COHERE_EMBED_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    SIMILARITY_THRESHOLD,
    TOP_K_CHUNKS,
)
from app.models import DocumentChunk


@lru_cache(maxsize=1)
def get_cohere_client() -> cohere.Client:
    return cohere.Client(api_key=COHERE_API_KEY)


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE_CHARS
        chunks.append(text[start:end])
        start = end - CHUNK_OVERLAP_CHARS
        if start <= 0:
            break
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed document chunks for storage/indexing."""
    client = get_cohere_client()
    response = client.embed(
        texts=texts,
        model=COHERE_EMBED_MODEL,
        input_type="search_document",
        embedding_types=["float"],
    )
    return response.embeddings.float


def embed_query(text: str) -> list[float]:
    """Embed an employee's question for similarity search."""
    client = get_cohere_client()
    response = client.embed(
        texts=[text],
        model=COHERE_EMBED_MODEL,
        input_type="search_query",
        embedding_types=["float"],
    )
    return response.embeddings.float[0]


def retrieve_relevant_chunks(db: Session, question: str, top_k: int = TOP_K_CHUNKS):
    """Return list of (DocumentChunk, cosine_similarity) sorted by relevance."""
    query_embedding = embed_query(question)
    # cosine_distance = 1 - cosine_similarity for normalized vectors
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)
    stmt = select(DocumentChunk, distance.label("distance")).order_by(distance).limit(top_k)
    results = db.execute(stmt).all()
    return [(chunk, 1 - dist) for chunk, dist in results]


def generate_answer(question: str, context_chunks: list[str]) -> tuple[str | None, bool]:
    """Ask Groq to answer strictly from context. Returns (answer, is_confident)."""
    context = "\n\n---\n\n".join(context_chunks)
    system_prompt = (
        "You are an HR policy assistant. Answer the employee's question using ONLY "
        "the provided policy context. If the context does not contain enough "
        "information to confidently answer, respond with exactly: NOT_FOUND"
    )
    user_prompt = f"Policy context:\n{context}\n\nQuestion: {question}"

    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=500,
    )
    answer = response.choices[0].message.content.strip()
    if answer == "NOT_FOUND" or not answer:
        return None, False
    return answer, True


def answer_question(db: Session, question: str) -> dict:
    """Full RAG pipeline. Returns dict with keys: answer, confident, sources."""
    matches = retrieve_relevant_chunks(db, question)

    if not matches or matches[0][1] < SIMILARITY_THRESHOLD:
        return {"answer": None, "confident": False, "sources": []}

    context_chunks = [chunk.chunk_text for chunk, _ in matches]
    answer, confident = generate_answer(question, context_chunks)

    sources = []
    if confident:
        seen = set()
        for chunk, _ in matches:
            filename = chunk.document.filename
            if filename not in seen:
                seen.add(filename)
                sources.append(filename)

    return {"answer": answer, "confident": confident, "sources": sources}
