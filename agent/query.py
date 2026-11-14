"""Answers a question using only what's in the indexed documents.

Retrieves the most relevant chunks, hands them to the LLM with an explicit
instruction to cite sources and to say it doesn't know rather than guess
when the retrieved context doesn't actually answer the question.
"""

from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agent.ingest import load_index
from agent.llm import get_llm

SYSTEM_PROMPT = (
    "Answer the question using ONLY the context provided below, which comes from the "
    "company's internal documents. Do not use outside knowledge. Cite the source file "
    "for each claim like this: (source: filename.md). If the context doesn't actually "
    "answer the question, say clearly that you don't have that information instead of "
    "guessing or making something up."
)

_vectorstore = None


def _get_vectorstore():
    # Open the index once per session, not once per question.
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_index()
    return _vectorstore


def answer_question(question: str, k: int = 4, model: str | None = None, llm=None, vectorstore=None) -> dict:
    vectorstore = vectorstore or _get_vectorstore()
    results = vectorstore.similarity_search(question, k=k)

    if not results:
        return {"answer": "I don't have any documents indexed yet.", "sources": [], "chunks_used": 0, "passages": []}

    context_blocks = []
    sources = []
    passages = []
    for doc in results:
        source_name = Path(doc.metadata.get("source", "unknown")).name
        context_blocks.append(f"[Source: {source_name}]\n{doc.page_content}")
        sources.append(source_name)
        passages.append({"source": source_name, "text": doc.page_content})

    context = "\n\n---\n\n".join(context_blocks)
    llm = llm or get_llm(model)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
    ]
    response = llm.invoke(messages)

    return {
        "answer": response.text,
        "sources": sorted(set(sources)),
        "chunks_used": len(results),
        # The exact text the answer was written from, in retrieval order,
        # so a UI can show the evidence next to the answer.
        "passages": passages,
    }
