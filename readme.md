# NCERT RAG Question Answering System

## Overview
This project implements a Retrieval-Augmented Generation (RAG) pipeline 
using NCERT textbooks. Text is extracted from PDF documents, converted 
into embeddings, stored in PostgreSQL with pgvector, and retrieved using 
semantic search to answer student questions accurately.

## Tech Stack
* Python 3.11.9
* PostgreSQL + pgvector (Docker)
* Sentence Transformers — BAAI/bge-base-en-v1.5
* Cohere command-r-plus-08-2024
* PyMuPDF
* FastAPI

## Project Phases

### Phase 1 — Data Pipeline (Completed)
* PDF text extraction from 15 NCERT Science chapters
* Header and footer removal using block coordinates
* Text chunking with 500 char size and 100 char overlap
* Embedding generation — 1311 chunks, 768 dimensions each

### Phase 2 — Vector Database and Search (In Progress)
* Store embeddings in PostgreSQL using pgvector
* HNSW index for fast similarity search
* Cosine similarity based chunk retrieval

### Phase 3 — Answer Generation
* Prompt construction with retrieved context
* Cohere API integration for final answer
* FastAPI endpoint for question answering

### Phase 4 — Optimisation
* Query caching
* Logging and error handling
* Response quality improvements
* API documentation

### Phase 5 — Frontend and Integration
* UI with Tailwind CSS
* Full pipeline integration
* Deployment

## Sample Questions
* What is photosynthesis?
* Explain the water cycle.
* What are the causes of soil erosion?
* What is banking of roads?