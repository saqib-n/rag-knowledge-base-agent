"""Help centre screen for the RAG knowledge base agent.

Opens a docs-style page in the browser: the company documents on the left,
questions and answers in the middle, and the exact passages each answer was
built from on the right. Same retrieval and answering code as ask.py. If
the index hasn't been built yet, the first question builds it.

Run:
    python app.py
"""

import logging
import os
import threading
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from agent import ingest, query
from agent.llm import DEFAULT_MODEL

load_dotenv()

logger = logging.getLogger("rag-agent")
app = FastAPI(title="RAG Knowledge Base Agent")
WEB_DIR = Path(__file__).resolve().parent / "web"
_index_lock = threading.Lock()


class Question(BaseModel):
    question: str = Field(min_length=2, max_length=1000)


def rebuild_index() -> int:
    with _index_lock:
        _, chunks = ingest.build_index()
        query._vectorstore = None  # make the next question open the fresh index
        return chunks


def ask(question: str) -> dict:
    if not ingest.INDEX_DIR.exists():
        rebuild_index()
    return query.answer_question(question)


@app.get("/", include_in_schema=False)
def help_centre():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/info")
def info():
    return {"model": os.getenv("LLM_MODEL") or DEFAULT_MODEL, "embeddings": ingest.EMBEDDING_MODEL, "index_built": ingest.INDEX_DIR.exists()}


@app.get("/api/documents")
def documents():
    return [{"name": Path(d.metadata["source"]).name, "text": d.page_content} for d in ingest.load_documents()]


@app.post("/api/index")
def build():
    started = time.perf_counter()
    try:
        chunks = rebuild_index()
    except Exception as exc:
        logger.exception("Index build failed")
        return JSONResponse(status_code=500, content={"error": f"Could not build the index ({type(exc).__name__})."})
    return {"chunks": chunks, "seconds": round(time.perf_counter() - started, 1)}


@app.post("/api/ask")
def ask_endpoint(body: Question):
    started = time.perf_counter()
    try:
        result = ask(body.question.strip())
    except Exception as exc:
        logger.exception("Answering failed")
        detail = str(exc).splitlines()[0][:200] if str(exc) else ""
        return JSONResponse(status_code=502, content={"error": f"The agent could not answer ({type(exc).__name__}: {detail})."})
    return {**result, "seconds": round(time.perf_counter() - started, 1)}


if __name__ == "__main__":
    import webbrowser

    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    uvicorn.run(app, host="127.0.0.1", port=port)
