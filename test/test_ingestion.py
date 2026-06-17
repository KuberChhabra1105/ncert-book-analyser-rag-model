import sys
import os

# path to import files from src folder
sys.path.append(os.path.join(os.path.dirname(__file__),'..','src'))

from ingestion import extract_all_pdfs

# Extract all PDFs from science folder
results = extract_all_pdfs("data/pdfs/science", "science")

# Show sample result
print("\nSample result:")
print("Filename   :", results[4]["filename"])
print("Subject    :", results[4]["subject"])
print("Page Number:", results[4]["page_number"])
print("Text sample:", results[4]["text"][:200])