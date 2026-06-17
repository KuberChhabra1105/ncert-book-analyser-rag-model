from sentence_transformers import SentenceTransformer


def load_embedding_model():
    """
    Loads the BGE embedding model from HuggingFace.
    
    Output : SentenceTransformer model object
    """

    print("Loading embedding model...")

    model = SentenceTransformer("BAAI/bge-base-en-v1.5")

    print("Model loaded!")
    print("Embedding dimensions:", model.get_embedding_dimension())
    return model


def generate_embeddings(chunks, model):
    """
    Generates embeddings for all chunks.

    Normalize all embeddings vectors the same length (magnitude = 1).
    This makes cosine similarity search more accurate and consistent.
    Instead of processing one chunk at a time, we process 32 at once.


    Input  : chunks - list of chunk dicts from chunking.py
             model  - loaded SentenceTransformer model
    Output : list of chunk dicts with embedding added
    """

    print(f"Generating embeddings for {len(chunks)} chunks...")

    # Extract just the text from each chunk for encoding
    texts = [chunk["text"] for chunk in chunks]

    # Generate all embeddings at once
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    print("Embeddings generated!")
    print("Embeddings shape:", embeddings.shape)

    # Attach embedding to each chunk dict
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()

    return chunks