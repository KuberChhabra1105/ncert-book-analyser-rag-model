from fastapi import FastAPI
from pydantic import BaseModel
from embeddings import load_embedding_model
from database import get_connection
from retrieval import retrieve_relevant_chunks
from llm import get_answer

# Initialize FastAPI app
app = FastAPI()

# Load model and database connection once at startup
# Not on every request — too slow
model = load_embedding_model()
conn = get_connection()


# Request body structure
class QuestionRequest(BaseModel):
    question: str


# Response body structure
class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list


@app.post("/ask")
def ask_question(request: QuestionRequest):
    """
    Accepts a question and returns an answer.

    Input  : JSON body with question field
    Output : JSON with question, answer, and sources
    """

    # Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(
        request.question,
        model,
        conn
    )

    # Get answer from Cohere
    answer = get_answer(request.question, chunks)

    # Build sources list for response
    sources = []

    for chunk in chunks:
        sources.append({
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "similarity": chunk["similarity"]
        })

    return AnswerResponse(
        question=request.question,
        answer=answer,
        sources=sources
    )


@app.get("/health")
def health_check():
    """
    Simple endpoint to verify API is running.
    """
    return {"status": "ok"}