# NCERT RAG Question Answering System

## Overview

This project implements a Retrieval-Augmented Generation (RAG) pipeline using NCERT textbooks. 
Text is extracted from PDF documents, converted into embeddings, stored in PostgreSQL with pgvector, and retrieved using semantic search.

## Tech Stack

* Python
* PostgreSQL + pgvector
* Sentence Transformers (BGE Base)
* Ollama (Llama 3.1)
* PyMuPDF

## Current Status

### Completed

* Document ingestion from NCERT PDFs
* Text preprocessing and chunking
* Embedding generation
* Vector storage in PostgreSQL
* Semantic retrieval workflow

### In Progress

* Answer generation validation using an open-source LLM
* Prompt tuning and response quality testing

## Sample Questions

* What is photosynthesis?
* Explain the water cycle.
* What are the causes of soil erosion?
* What is banking of roads?

## Run

```bash
pip install pymupdf sentence-transformers psycopg2-binary pgvector ollama
python rag_pipeline.py
```
