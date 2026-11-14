from fastapi.testclient import TestClient
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

import app as web
from agent import ingest, query


def test_help_centre_builds_index_then_answers(monkeypatch, tmp_path):
    monkeypatch.setattr(ingest, "INDEX_DIR", tmp_path / "index")
    monkeypatch.setattr(ingest, "_embeddings", DeterministicFakeEmbedding(size=64))
    monkeypatch.setattr(query, "_vectorstore", None)
    real_answer = query.answer_question
    llm = GenericFakeChatModel(messages=iter([AIMessage(content="30 days (source: return_policy.md)")]))
    monkeypatch.setattr(query, "answer_question", lambda q: real_answer(q, llm=llm))
    client = TestClient(web.app)

    assert "Ask the handbook" in client.get("/").text
    assert len(client.get("/api/documents").json()) == 3
    assert client.get("/api/info").json()["index_built"] is False

    # The first question builds the missing index on the fly.
    result = client.post("/api/ask", json={"question": "what's the return window"}).json()
    assert result["answer"].startswith("30 days")
    assert len(result["passages"]) == result["chunks_used"] == 4
    assert all(p["source"].endswith(".md") and p["text"] for p in result["passages"])
    assert (tmp_path / "index").exists()

    assert client.post("/api/index").json()["chunks"] > 0
    assert client.post("/api/ask", json={"question": ""}).status_code == 422
