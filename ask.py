"""Ask questions against the indexed documents from the terminal.

Run 'python build_index.py' first if you haven't already, then:
    python ask.py

Try:
    what's the return window
    do you ship to Canada
    can I work remote 5 days a week
    what's your policy on cryptocurrency payments   (should say it doesn't know)
"""

from dotenv import load_dotenv

from agent.query import answer_question

load_dotenv()


def main():
    print("RAG Knowledge Base Agent - type 'exit' to quit\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        result = answer_question(question)
        print(f"\nAgent: {result['answer']}")
        print(f"Sources: {', '.join(result['sources']) or 'none'}\n")


if __name__ == "__main__":
    main()
