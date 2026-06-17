import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


def retrieve_relevant_chunks(question, model, conn, top_k=5):
    """
    Finds most relevant chunks for a given question.

    How it works:
    1. Convert question to embedding using same BGE model
    2. Compare question embedding with all chunk embeddings
    3. Return top_k most similar chunks

    Why search_query prefix?
    BGE model works better when question has this prefix.
    Documents dont need it — only queries.

    Input  : question - user's question string
             model    - loaded BGE model
             conn     - database connection
             top_k    - how many chunks to return
    Output : list of dicts with content and metadata
    """

    # Add query prefix — BGE model specific requirement
    query_text = "Represent this sentence for searching relevant passages: " + question

    # Convert question to embedding
    question_embedding = model.encode(
        query_text,
        normalize_embeddings=True
    ).tolist()

    cur = conn.cursor()

    # Search database for similar chunks
    # <=> is cosine distance operator in pgvector
    # 1 - distance = similarity score
    cur.execute("""
        SELECT
            content,
            filename,
            page_number,
            1 - (embedding <=> %s::vector) AS similarity
        FROM ncert_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (question_embedding, question_embedding, top_k))

    rows = cur.fetchall()
    cur.close()

    # Format results as list of dicts
    results = []

    for row in rows:
        results.append({
            "content": row[0],
            "filename": row[1],
            "page_number": row[2],
            "similarity": round(row[3], 4)
        })

    return results