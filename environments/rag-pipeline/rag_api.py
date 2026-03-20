from fastapi import FastAPI
from pydantic import BaseModel
import os

from openai import OpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

app = FastAPI(title="AI Security Training Lab - RAG Pipeline")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")

embedding = OpenAIEmbeddings()
vectorstore = Chroma(
    collection_name="rag_lab",
    embedding_function=embedding,
)


class IngestRequest(BaseModel):
    text: str


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "ok", "service": "rag-pipeline"}


@app.get("/health")
def health():
    return {"healthy": True}


@app.post("/ingest")
def ingest(req: IngestRequest):
    splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_text(req.text)
    vectorstore.add_texts(chunks)

    return {
        "message": "Document ingested successfully",
        "chunks_added": len(chunks)
    }


@app.post("/query")
def query(req: QueryRequest):
    docs = vectorstore.similarity_search(req.question, k=3)
    retrieved_context = [doc.page_content for doc in docs]
    context_block = "\n\n".join(retrieved_context)

    prompt = f"""
You are a helpful assistant answering questions based only on the retrieved context below.

Retrieved context:
{context_block}

User question:
{req.question}

Answer the user's question using the retrieved context.
"""

    response = client.responses.create(
        model=model_name,
        input=prompt,
    )

    answer_text = response.output_text

    return {
        "question": req.question,
        "retrieved_context": retrieved_context,
        "answer": answer_text
    }