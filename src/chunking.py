def split_into_chunks(text, chunk_size=500, overlap=100):
    """
    Takes a long text and splits it into smaller overlapping chunks.

    Input  : text       - full text string to split
             chunk_size - maximum characters per chunk (default 500)
             overlap    - how many characters to repeat between chunks (default 100)
    Output : list of text strings (chunks)
    """

    chunks = []
    start = 0

    while start < len(text):

        # Calculate end position of this chunk
        end = start + chunk_size

        # If we are not at the last chunk
        if end < len(text):

            # Find the last space before end
            # This avoids cutting a word in the middle
            last_space = text.rfind(" ", start, end)

            if last_space != -1:
                end = last_space

        # Extract this chunk and remove extra spaces
        chunk = text[start:end].strip()

        # Only add chunks that have meaningful content
        if len(chunk) > 50:
            chunks.append(chunk)

        # Move start back by overlap amount
        # This creates the overlapping effect
        start = end - overlap

    return chunks


def chunk_all_pages(pages_data, chunk_size=500, overlap=100):
    """
    Takes all extracted pages and chunks each page's text.
    Keeps metadata attached to every chunk.

    Input  : pages_data  - list of dicts from ingestion.py
             chunk_size  - characters per chunk
             overlap     - overlapping characters
    Output : list of dicts with chunk text and metadata
    """

    all_chunks = []

    for page in pages_data:

        # Split this page's text into chunks
        chunks = split_into_chunks(
            page["text"],
            chunk_size,
            overlap
        )

        # Attach metadata to every chunk
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "filename": page["filename"],
                "subject": page["subject"],
                "page_number": page["page_number"],
                "chunk_index": i,
                "text": chunk
            })

    print(f"Total chunks created: {len(all_chunks)}")

    return all_chunks