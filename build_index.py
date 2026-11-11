"""Builds the vector index from everything in data/documents/.

Run this once after adding or changing documents:
    python build_index.py

Re-run it any time documents change, it rebuilds the whole index rather
than updating it incrementally, which is fine for a document set this
size and much simpler to reason about.
"""

from agent.ingest import INDEX_DIR, build_index


def main():
    print("Indexing documents...")
    _, chunk_count = build_index()
    print(f"Done. Indexed {chunk_count} chunks into {INDEX_DIR}")


if __name__ == "__main__":
    main()
