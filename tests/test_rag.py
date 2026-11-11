from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from agent import ingest
from agent.query import answer_question


def use_temp_index(monkeypatch, tmp_path):
    monkeypatch.setattr(ingest, "INDEX_DIR", tmp_path / "index")
    monkeypatch.setattr(ingest, "_embeddings", DeterministicFakeEmbedding(size=64))


def test_loads_the_sample_documents():
    names = sorted({d.metadata["source"].replace("\\", "/").split("/")[-1] for d in ingest.load_documents()})
    assert names == ["remote_work_policy.md", "return_policy.md", "shipping_policy.md"]


def test_rebuild_does_not_duplicate_chunks(monkeypatch, tmp_path):
    use_temp_index(monkeypatch, tmp_path)
    first, chunks = ingest.build_index()
    assert first._collection.count() == chunks
    second, _ = ingest.build_index()
    assert second._collection.count() == chunks


def test_answer_lists_its_sources(monkeypatch, tmp_path):
    use_temp_index(monkeypatch, tmp_path)
    store, _ = ingest.build_index()
    llm = GenericFakeChatModel(messages=iter([AIMessage(content="30 days (source: return_policy.md)")]))
    result = answer_question("what's the return window", llm=llm, vectorstore=store)
    assert result["answer"].startswith("30 days")
    assert result["chunks_used"] == 4
    assert all(s.endswith(".md") for s in result["sources"])
