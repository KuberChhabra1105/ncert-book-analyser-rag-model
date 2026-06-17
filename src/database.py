import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection():
    """
    Creates and returns a PostgreSQL connection.
    Reads all credentials from .env file.
    """

    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn

    except psycopg2.OperationalError as e:
        print("Database connection failed:", e)
        raise


def setup_database(conn):
    """
    Enables pgvector and creates the chunks table.
    IF NOT EXISTS means safe to run multiple times.
    """

    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ncert_chunks (
            id          SERIAL PRIMARY KEY,
            subject     TEXT,
            filename    TEXT,
            page_number INTEGER,
            chunk_index INTEGER,
            content     TEXT,
            embedding   vector(768)
        );
    """)

    conn.commit()
    cur.close()

    print("Database setup complete.")


def insert_chunks(conn, chunks):
    """
    Inserts all chunks with embeddings into database.

    Why execute_values?
    Sends all rows in one database call instead of
    1311 separate calls — much faster.
    """

    cur = conn.cursor()

    data = []

    for chunk in chunks:
        data.append((
            chunk["subject"],
            chunk["filename"],
            chunk["page_number"],
            chunk["chunk_index"],
            chunk["text"],
            chunk["embedding"]
        ))

    execute_values(
        cur,
        """
        INSERT INTO ncert_chunks
            (subject, filename, page_number, chunk_index, content, embedding)
        VALUES %s
        """,
        data
    )

    conn.commit()
    cur.close()

    print(f"Inserted {len(chunks)} chunks into database.")


def create_hnsw_index(conn):
    """
    Creates HNSW index on embedding column.
    Build index after inserting data — faster this way.
    Default values m=16, ef_construction=64 are
    fine for our dataset size of 1311 chunks.
    """

    cur = conn.cursor()

    cur.execute("""
        CREATE INDEX IF NOT EXISTS ncert_chunks_embedding_idx
        ON ncert_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    conn.commit()
    cur.close()

    print("HNSW index created.")


def get_table_count(conn):
    """
    Returns total rows in ncert_chunks.
    Used to verify insertion worked correctly.
    """

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM ncert_chunks;")
    count = cur.fetchone()[0]
    cur.close()

    return count