import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingestion import extract_all_pdfs
from chunking import chunk_all_pages
from embeddings import load_embedding_model, generate_embeddings

# Step 1 - Extract
pages_data = extract_all_pdfs("data/pdfs/science", "science")

# Step 2 - Chunk
all_chunks = chunk_all_pages(pages_data)

# Step 3 - Load model
model = load_embedding_model()

# Step 4 - Generate embeddings for first 5 chunks only (for testing)
test_chunks = all_chunks[:5]
test_chunks = generate_embeddings(test_chunks, model)

# Show results
print("\nSample embedding result:")
print("Filename   :", test_chunks[0]["filename"])
print("Page Number:", test_chunks[0]["page_number"])
print("Text       :", test_chunks[0]["text"][:100])
print("Embedding size  :", len(test_chunks[0]["embedding"]))
print("First 5 values  :", test_chunks[0]["embedding"][:5])
