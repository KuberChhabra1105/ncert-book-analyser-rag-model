import cohere
from dotenv import load_dotenv
import os

load_dotenv()


def get_answer(question, retrieved_chunks):
    """
    Takes a question and relevant chunks,
    builds a prompt and gets answer from Cohere.

    Input  : question         - user's question string
             retrieved_chunks - list of dicts from retrieval.py
    Output : answer string
    """

    co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))

    # Build context from retrieved chunks
    context = ""

    for i, chunk in enumerate(retrieved_chunks):
        context += f"Passage {i+1} "
        context += f"(Source: {chunk['filename']}, Page {chunk['page_number']}):\n"
        context += chunk["content"]
        context += "\n\n"

    # System prompt — tells model how to behave
    system_prompt = """You are a helpful assistant for students studying from NCERT textbooks.
    Use the provided passages to answer the question as clearly as possible.
    At the end of your answer mention the source file and page number.
    Keep the answer simple and easy to understand for a student."""

    # User prompt — question + context
    user_prompt = f"""Passages:
{context}
Question: {question}

Answer:"""

    response = co.chat(
        model="command-r-plus-08-2024",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.message.content[0].text
