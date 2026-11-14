<div align="center">

<h1>RAG Knowledge Base Agent</h1>

<p><b>Ask questions about your own documents. Every answer names the file it came from, or says plainly that the documents don't cover it.</b></p>

<p>
  <a href="https://github.com/saqib-n/rag-knowledge-base-agent/actions/workflows/tests.yml"><img src="https://github.com/saqib-n/rag-knowledge-base-agent/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python: 3.12+">
  <img src="https://img.shields.io/badge/LangChain-1.x-1C3C3C" alt="LangChain: 1.x">
  <img src="https://img.shields.io/badge/vector%20store-Chroma-FF6446" alt="vector store: Chroma">
  <img src="https://img.shields.io/badge/models-OpenAI%20%7C%20Claude%20%7C%20Gemini-444444" alt="models: OpenAI | Claude | Gemini">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2E7D32" alt="license: MIT"></a>
</p>

<p>
  <a href="#what-it-does">What it does</a> &nbsp;|&nbsp;
  <a href="#how-it-works">How it works</a> &nbsp;|&nbsp;
  <a href="#sample-run">Sample run</a> &nbsp;|&nbsp;
  <a href="#quick-start">Quick start</a> &nbsp;|&nbsp;
  <a href="#configuration">Configuration</a> &nbsp;|&nbsp;
  <a href="#roadmap">Roadmap</a>
</p>

</div>

<br>

<h2>See it in action</h2>

<p align="center"><img src="demo/demo.gif" alt="Help centre screen: answers with clickable sources, the retrieved passages, and the source document with the used lines highlighted" width="100%"></p>

<p align="center"><sub>Recorded in the built-in help centre from a real run on Google Gemini (<code>gemini-3.1-flash-lite</code>) on 14 November 2026. Nothing is scripted. Only the time spent waiting for the model is fast-forwarded, and the real response times are shown on screen. <a href="demo/demo.mp4">Download the MP4</a>.</sub></p>

<p>Run <code>python app.py</code> and it opens a help centre where answers link to their sources, with the exact passages the answer was built from and the source document highlighted. It is the same agent code as the command line version, with a screen on top.</p>

<h2>The problem</h2>

<p>Company knowledge lives in policies, handbooks and help docs that nobody can search quickly. Generic chatbots answer confidently from what they already know, which is not your policy.</p>

<p>A knowledge base assistant is only worth having if people can trust it. That means answers they can check, and an honest "I don't know" when the documents are silent.</p>

<h2>What it does</h2>

<table>
  <tr><th align="left">Capability</th><th align="left">What that means in practice</th></tr>
  <tr><td><b>Your documents</b></td><td>Reads every <code>.md</code>, <code>.txt</code> and <code>.pdf</code> in <code>data/documents/</code>.</td></tr>
  <tr><td><b>Sources on every answer</b></td><td>Each answer cites the file it came from, so anyone can check it.</td></tr>
  <tr><td><b>Admits what it doesn't know</b></td><td>If the documents don't cover a question, it says so instead of guessing.</td></tr>
  <tr><td><b>Free, local embeddings</b></td><td>Documents are embedded on your own machine with FastEmbed. Indexing and search need no API key and cost nothing.</td></tr>
  <tr><td><b>Clean re-indexing</b></td><td>Add or change documents and rebuild. The old index is cleared first, so nothing is counted twice.</td></tr>
</table>

<h2>How it works</h2>

<pre>
build_index.py:  documents --&gt; chunks (800 chars) --&gt; local embeddings --&gt; Chroma index

ask.py:          question --&gt; embed --&gt; 4 closest chunks --&gt; model --&gt; answer + sources
</pre>

<p>Documents are split into overlapping chunks and stored in a Chroma vector database on disk. When you ask a question, the four most relevant chunks are sent to the model with strict instructions to answer only from them and to cite the file.</p>

<p>Only the final answer step calls a paid model, so running costs stay low even with a large document set.</p>

<h2>Decisions I made on purpose</h2>

<h3>"I don't know" is a feature</h3>

<p>A RAG system that answers confidently from weak retrieval is worse than nothing. It looks authoritative and it is wrong, and the person asking can't tell. The prompt requires the model to admit gaps, and the citation rule makes an invented answer obvious, because there is nothing to point to.</p>

<h3>Mixed sample documents</h3>

<p>The samples are a shipping policy, a return policy and an internal remote-work policy. Customer-facing and internal documents are mixed on purpose, to show it isn't tuned to one kind of text.</p>

<h2>Sample run</h2>

<p>The first answer is from a real run on Google Gemini:</p>

<pre>
$ python ask.py
You: How many days do I have to return an item?
Agent: You have 30 days from delivery to return an item for a full refund,
provided the item is unused, unworn, and in its original packaging with tags
attached (source: return_policy.md).
Sources: return_policy.md, shipping_policy.md

You: what's your policy on cryptocurrency payments
Agent: I don't have information about cryptocurrency payments in the
documents I have access to.
</pre>

<h2>Quick start</h2>

<p>You need Python 3.12 or newer and an API key from OpenAI, Anthropic or Google Gemini.</p>

<pre>
pip install -r requirements.txt
python build_index.py       # no API key needed
cp .env.example .env        # on Windows: copy .env.example .env
# open .env and paste your API key
python app.py               # opens the help centre at http://localhost:8000
python ask.py
</pre>

<p>The first run downloads a small embedding model (about 80 MB). After that it starts quickly. To use your own documents, put them in <code>data/documents/</code> and run <code>build_index.py</code> again.</p>

<h2>Configuration</h2>

<p>Everything is set in <code>.env</code>. Copy <code>.env.example</code> to start.</p>

<table>
  <tr><th align="left">Variable</th><th align="left">Required</th><th align="left">Purpose</th></tr>
  <tr><td><code>LLM_MODEL</code></td><td>Yes</td><td>Which model to use, as <code>provider:model</code>. Default <code>openai:gpt-5.5</code>. Also works with <code>anthropic:claude-opus-5-5</code> or <code>google_genai:gemini-3.5-flash</code>.</td></tr>
  <tr><td><code>OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY</code></td><td>One of them</td><td>The key for whichever provider you picked.</td></tr>
</table>

<h2>Project structure</h2>

<pre>
rag-knowledge-base-agent/
  .env.example        # copy to .env and add your key
  ask.py              # question and answer chat
  build_index.py      # builds the vector index
  app.py            # browser help centre, the same agent with a UI
  case_study.md       # longer write-up of the design
  README.md
  requirements.txt    # dependencies
  agent/
    ingest.py         # loading, chunking and local embeddings
    llm.py            # picks the model from LLM_MODEL
    query.py          # retrieval and the answer prompt
  data/
    documents/        # sample policies, replace with your own
  demo/               # recording of a live run (GIF, MP4 and a screenshot)
  tests/              # pytest suite, runs without any API key
  web/
    index.html          # the help centre, one file, no build step
</pre>

<h2>Built with</h2>

<p>Python &nbsp;&middot;&nbsp; LangChain &nbsp;&middot;&nbsp; Chroma &nbsp;&middot;&nbsp; FastEmbed &nbsp;&middot;&nbsp; pypdf &nbsp;&middot;&nbsp; OpenAI / Anthropic / Gemini</p>

<h2>Tests</h2>

<pre>
pip install -r requirements-dev.txt
pytest
</pre>

<p>Four tests cover document loading, rebuilding the index without duplicates, and answers coming back with their sources. They use a stand-in embedding model, so nothing is downloaded, plus the browser screen and its API. None of the tests call a model or need an API key, so they run on GitHub Actions on every push. The badge at the top shows the latest result.</p>

<h2>Roadmap</h2>

<p>What I would build next if a client took this into production:</p>
<ul>
  <li>A web chat interface, or Slack and Microsoft Teams bots, for internal use</li>
  <li>Syncing documents from Google Drive, Notion or SharePoint</li>
  <li>Access control, so each person only searches the documents they are allowed to see</li>
  <li>Incremental indexing for thousands of files, and better handling of tables</li>
  <li>A multilingual embedding model for documents in other languages</li>
</ul>

<h2>More from this series</h2>

<p>Nine production-minded AI agents, each solving one business problem properly.</p>

<table>
  <tr><td><a href="https://github.com/saqib-n/ai-research-report-agent"><b>Research Report Agent</b></a></td><td>Researches a topic, notices its own gaps, and writes a report with a source for every claim.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/ai-sales-outreach-agent"><b>AI Sales Outreach Agent</b></a></td><td>Personalised cold emails and follow-ups, with a human approving every send.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/ecommerce-automation-agent"><b>E-commerce Order and Inventory Agent</b></a></td><td>Shopify order, stock and returns assistant, plus a monitor that warns you before stock runs out.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/email-triage-agent"><b>Email Triage Agent</b></a></td><td>Sorts an inbox into four buckets and gives each one a different level of autonomy.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/lead-qualification-crm-agent"><b>Lead Qualification Agent</b></a></td><td>Scores inbound leads against your own rubric and pushes the good ones to HubSpot.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/multi-agent-customer-support"><b>Multi-Agent Customer Support</b></a></td><td>A router plus specialist agents for orders, refunds, FAQs and human handoff.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/recruiting-screening-agent"><b>Resume Screening Agent</b></a></td><td>Ranks resumes against a job description with evidence, and guards against common bias.</td></tr>
  <tr><td><a href="https://github.com/saqib-n/whatsapp-support-agent"><b>WhatsApp Support Agent</b></a></td><td>A WhatsApp Cloud API agent that checks orders, answers FAQs and escalates to a person.</td></tr>
</table>

<h2>Work with me</h2>

<p>I'm Saqib Nawaz, founder of WolfXense AI. I build AI agents and automations for businesses, with Python, LangChain, LangGraph and n8n, and connect them to the tools teams already use, like CRMs, Shopify, Slack, email and WhatsApp.</p>

<p>If your team keeps asking the same questions your documents already answer, I can build this on your own files and put it where your team already works.</p>

<p><a href="https://www.upwork.com/freelancers/~01de008504a38baf28"><b>Hire me on Upwork</b></a> &nbsp;|&nbsp; <a href="https://github.com/saqib-n"><b>More of my work on GitHub</b></a></p>

<hr>

<p><sub>Released under the <a href="LICENSE">MIT License</a>. A longer write-up of the design is in <a href="case_study.md">case_study.md</a>.</sub></p>
