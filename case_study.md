# RAG Knowledge Base Agent

## Portfolio entry

A question-answering agent over a client's own documents that names its source for every claim and says plainly when the documents don't cover something, rather than producing a confident answer from thin context. Documents are chunked and embedded locally with FastEmbed, so indexing and retrieval cost nothing and need no API key, and only the final answer step calls an LLM. Chroma for the vector store, LangChain for the retrieval pipeline.

**Stack:** Python, LangChain, Chroma, FastEmbed, OpenAI / Anthropic / Gemini

---

## Every business has this pile

Policy PDFs, an internal wiki, a product manual, three years of support tickets. Technically searchable. Practically ignored, because digging through a shared drive is slower than asking the person who already knows.

"Build us a chatbot trained on our documents" is one of the most common requests in this space, and most of the time the request is reasonable and the delivered thing is unreliable.

## The failure mode this is built around

A RAG system that answers confidently from weak retrieval is worse than no system at all. It looks authoritative. The person asking has no way to tell a well-sourced answer from a fabricated one. And the first time someone acts on a made-up policy, the client stops trusting the whole thing.

So two constraints shape the query step:

The prompt says outright that if the retrieved context doesn't answer the question, say so instead of guessing.

And every claim has to cite its source file, which makes fabrication easy to catch, there's nothing to point at.

Asked about a cryptocurrency payment policy that doesn't exist anywhere in the sample documents, it says it doesn't have that information. That behaviour is the deliverable as much as the correct answers are.

## Local embeddings, and why

Indexing runs through FastEmbed on the machine. No embeddings API, no per-chunk cost, no key required.

Two practical reasons. A client can watch the thing index their documents and test retrieval quality before spending anything, which shortens the trust conversation a lot. And the only place a paid API is needed is answer generation, which is also the easiest piece to swap between providers if a client has a preference or a procurement constraint.

## Honest limits

Chunking is text-oriented and mangles tables, which matters if a client's documents are full of pricing grids.

There's no access control. Anyone who can ask a question can reach anything indexed, which becomes a problem the moment some documents are more sensitive than others, and that has to be enforced at retrieval time rather than bolted on after.

Re-indexing rebuilds everything from scratch. Fine for a few dozen files, wrong for a few thousand.

## For a real engagement

Incremental indexing, access control at retrieval, a Slack bot or web widget instead of a terminal, and a managed vector database once the document set outgrows local Chroma.

## My part

The retrieval pipeline, the decision to run embeddings locally, and the prompt and citation design that makes "I don't know" a real outcome rather than an afterthought.
