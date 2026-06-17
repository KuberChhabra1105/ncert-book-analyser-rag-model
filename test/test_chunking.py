import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingestion import extract_all_pdfs
from chunking import chunk_all_pages

# Step 1 - Extract pages
pages_data = extract_all_pdfs("data/pdfs/science", "science")

# Step 2 - Chunk all pages
all_chunks = chunk_all_pages(pages_data)

# Show statistics
lengths = [len(c["text"]) for c in all_chunks]

print("\nChunk Statistics:")
print("Total chunks :", len(all_chunks))
print("Min length   :", min(lengths))
print("Max length   :", max(lengths))
print("Avg length   :", sum(lengths) // len(lengths))

# Show sample chunk with metadata
print("\nSample Chunk:")
print("Filename   :", all_chunks[10]["filename"])
print("Subject    :", all_chunks[10]["subject"])
print("Page Number:", all_chunks[10]["page_number"])
print("Chunk Index:", all_chunks[10]["chunk_index"])
print("Text       :", all_chunks[10]["text"][:200])