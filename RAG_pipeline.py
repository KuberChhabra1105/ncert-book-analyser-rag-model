# Import required libraries
import re
import fitz
import ollama
import psycopg2
from sentence_transformers import SentenceTransformer

# Install required packages
!pip install pymupdf
!pip install sentence-transformers
!pip install psycopg2-binary
!pip install pgvector
!pip install ollama

# Load the document
pdf_file = fitz.open("science_class10.pdf")

print("total pages:", len(pdf_file))

# Read the first page
first_page = pdf_file[0]
text = first_page.get_text()

print(text)

# Check page blocks
first_page = pdf_file[0]
page_height = first_page.rect.height

print("page height in points:", page_height)

blocks = first_page.get_text("blocks")

print("number of blocks on first page:", len(blocks))
print("\nfirst block looks like:")
print(blocks[0])

# Extract text from all pages
all_text = []

for page_number in range(len(pdf_file)):
    page = pdf_file[page_number]
    height = page.rect.height

    blocks = page.get_text("blocks")

    page_text = ""

    for block in blocks:
        x0 = block[0]
        y0 = block[1]
        x1 = block[2]
        y1 = block[3]
        text = block[4]

        if y0 < height * 0.08:
            continue

        if y1 > height * 0.92:
            continue

        if len(text.strip()) < 20:
            continue

        page_text += text + " "

    if len(page_text.strip()) > 50:
        all_text.append(page_text.strip())

print("pages with content:", len(all_text))
print("\nsample from page 5:")
print(all_text[4][:400])

# Join extracted text
raw_text = " ".join(all_text)

print("raw text length:", len(raw_text))
print("\nbefore cleaning sample:")
print(raw_text[1000:1300])

# Clean the extracted text
cleaned = raw_text

cleaned = re.sub(r'(\w+)-\n(\w+)', r'\1\2', cleaned)
cleaned = re.sub(r'Fig\.?\s*\d+\.\d+', '', cleaned)
cleaned = re.sub(r'Table\s*\d+\.\d+', '', cleaned)
cleaned = re.sub(r' +', ' ', cleaned)
cleaned = re.sub(r'\n+', '\n', cleaned)

print("after cleaning sample:")
print(cleaned[1000:1300])
print("\ncleaned text length:", len(cleaned))

# Split text into chunks
chunk_size = 500
overlap = 100

chunks = []

start = 0

while start < len(cleaned):
    end = start + chunk_size

    if end < len(cleaned):
        last_space = cleaned.rfind(" ", start, end)
        if last_space != -1:
            end = last_space

    chunk = cleaned[start:end].strip()

    if len(chunk) > 50:
        chunks.append(chunk)

    start = end - overlap

print("total chunks created:", len(chunks))
print("\nchunk 0:")
print(chunks[0])
print("\nchunk 1:")
print(chunks[1])

# Check chunk statistics
lengths = [len(c) for c in chunks]

print("min chunk length:", min(lengths))
print("max chunk length:", max(lengths))
print("avg chunk length:", sum(lengths) // len(lengths))

# Load embedding model
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

print("model loaded")
print("embedding size:", model.get_sentence_embedding_dimension())

# Test embedding generation
test_embedding = model.encode("photosynthesis is the process of making food")

print("type:", type(test_embedding))
print("shape:", test_embedding.shape)
print("first 10 values:", test_embedding[:10])

# Create embeddings for all chunks
print("embedding", len(chunks), "chunks, this might take a minute...")

all_embeddings = model.encode(
    chunks,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

print("done!")
print("embeddings shape:", all_embeddings.shape)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="rag_db",
    user="postgres",
    password="mypassword"
)

cur = conn.cursor()

print("connected to database")

# Enable pgvector
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

conn.commit()

print("pgvector extension enabled")

# Create table for chunks
cur.execute("""
    CREATE TABLE IF NOT EXISTS ncert_chunks (
        id SERIAL PRIMARY KEY,
        subject TEXT,
        content TEXT,
        embedding vector(768)
    );
""")

conn.commit()

print("table created")

# Insert embeddings into database
for i in range(len(chunks)):
    cur.execute(
        "INSERT INTO ncert_chunks (subject, content, embedding) VALUES (%s, %s, %s)",
        (
            "science",
            chunks[i],
            all_embeddings[i].tolist()
        )
    )

conn.commit()

print("inserted", len(chunks), "chunks into database")

# Verify stored data
cur.execute("SELECT COUNT(*) FROM ncert_chunks;")

print("rows in table:", cur.fetchone()[0])

cur.execute(
    "SELECT id, subject, LEFT(content, 100) FROM ncert_chunks LIMIT 3;"
)

print("\nsample rows:")

for row in cur.fetchall():
    print(row)

# Create vector index
cur.execute("""
    CREATE INDEX IF NOT EXISTS chunks_vector_idx
    ON ncert_chunks
    USING hnsw (embedding vector_cosine_ops);
""")

conn.commit()

print("index created")

# Create question embedding
question = "What is photosynthesis?"

question_for_search = (
    "Represent this sentence for searching relevant passages: "
    + question
)

question_embedding = model.encode(
    question_for_search,
    normalize_embeddings=True
)

print("question embedded, shape:", question_embedding.shape)

# Retrieve relevant chunks
question_vector = question_embedding.tolist()

cur.execute(
    """
    SELECT
        id,
        content,
        1 - (embedding <=> %s::vector) as similarity
    FROM ncert_chunks
    ORDER BY embedding <=> %s::vector
    LIMIT 5;
    """,
    (question_vector, question_vector)
)

results = cur.fetchall()

print("top 5 most relevant chunks for:", question)
print()

for i, row in enumerate(results):
    chunk_id = row[0]
    content = row[1]
    score = row[2]

    print(f"--- result {i+1} | similarity: {score:.4f}")
    print(content[:300])
    print()

# Build context for the LLM
context = ""

for i, row in enumerate(results):
    context += f"Passage {i+1}:\n{row[1]}\n\n"

print("context we are giving to llm:")
print(context[:600])
print("...")

# Create the prompt
prompt = f"""You are a helpful assistant for students.
Use the following passages from NCERT textbooks to answer the question.
Only use information from the passages. If the answer is not in the passages, say you dont know.

Passages:
{context}

Question: {question}

Answer:"""

print("prompt ready, length:", len(prompt))

# Generate answer using LLM
response = ollama.chat(
    model="llama3.1",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    options={
        "temperature": 0.1
    }
)

answer = response["message"]["content"]

print("QUESTION:", question)
print()
print("ANSWER:", answer)

# Test sample questions
questions = [
    "What is photosynthesis?",
    "What is banking of roads?",
    "Explain the water cycle.",
    "What are the causes of soil erosion?"
]

for question in questions:

    q = (
        "Represent this sentence for searching relevant passages: "
        + question
    )

    q_embedding = model.encode(
        q,
        normalize_embeddings=True
    ).tolist()

    cur.execute(
        """
        SELECT content, 1 - (embedding <=> %s::vector) as score
        FROM ncert_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT 4;
        """,
        (q_embedding, q_embedding)
    )

    rows = cur.fetchall()

    ctx = ""

    for i, row in enumerate(rows):
        ctx += f"Passage {i+1}:\n{row[0]}\n\n"

    p = f"""Use the passages below to answer the question. Only use info from the passages.

Passages:
{ctx}
Question: {question}
Answer:"""

    resp = ollama.chat(
        model="llama3.1",
        messages=[
            {
                "role": "user",
                "content": p
            }
        ],
        options={
            "temperature": 0.1
        }
    )

    print("=" * 60)
    print("Q:", question)
    print("A:", resp["message"]["content"])
    print()

# Close database connection
cur.close()
conn.close()

print("done")