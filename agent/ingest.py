"""Loads documents, splits them into chunks, and builds/loads a local
Chroma vector index.

Embeddings run locally through FastEmbed (a small ONNX model, no torch, no
API key, no cost) so indexing and retrieval both work with zero external
dependencies. Only the final answer-writing step needs an LLM key, see
agent/query.py.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"
INDEX_DIR = Path(__file__).resolve().parent.parent / "chroma_index"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

_embeddings = None


class FastEmbedEmbeddings(Embeddings):
    """FastEmbed wrapped in LangChain's Embeddings interface.

    Uses FastEmbed directly rather than the langchain-community wrapper,
    since that package is no longer maintained.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.passage_embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.query_embed(text))).tolist()


def get_embeddings() -> Embeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = FastEmbedEmbeddings()
    return _embeddings


def load_documents() -> list[Document]:
    docs = []
    for path in sorted(DOCS_DIR.glob("**/*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            docs.append(Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": str(path)}))
        elif suffix == ".pdf":
            for page_number, page in enumerate(PdfReader(path).pages):
                text = page.extract_text() or ""
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": str(path), "page": page_number}))
    return docs


def build_index() -> tuple[Chroma, int]:
    docs = load_documents()
    if not docs:
        raise SystemExit(f"No documents found in {DOCS_DIR}. Add .md, .txt, or .pdf files there first.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)

    # Chroma.from_documents adds to whatever is already stored, so without
    # this every rebuild would index each document again on top of the old
    # copies. Clearing the collection keeps it a true rebuild.
    if INDEX_DIR.exists():
        Chroma(persist_directory=str(INDEX_DIR), embedding_function=get_embeddings()).delete_collection()

    vectorstore = Chroma.from_documents(
        chunks,
        embedding=get_embeddings(),
        persist_directory=str(INDEX_DIR),
    )
    return vectorstore, len(chunks)


def load_index() -> Chroma:
    if not INDEX_DIR.exists():
        raise SystemExit("No index found. Run 'python build_index.py' first.")
    return Chroma(persist_directory=str(INDEX_DIR), embedding_function=get_embeddings())
