import os
import sys
from pprint import pprint

# --- Add project root to path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------

try:
    from src.llm.litellm_gateway import setup_aws_credentials
    setup_aws_credentials()

    from src.rag.vector_store import search_vector_store
    from src.llm.litellm_gateway import LLMGateway
    from config.settings import LLM_RAG_MODEL
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


def run_rag_query(question: str):
    """Runs an InvoiceIQ RAG query using vector search and LLM generation."""
    print("Searching vector store for relevant context...")
    context = search_vector_store(question, top_k=3)

    if not context or context == "No relevant context found.":
        print("--- [InvoiceIQ RAG Answer] ---")
        print("No relevant content was found in the vector store.")
        return

    print("[InvoiceIQ] Context retrieved")
    print("Sending context to the LLM for answer generation...")
    try:
        rag_gateway = LLMGateway(model=LLM_RAG_MODEL)
        answer = rag_gateway.call_for_rag_generation(question, context)
        print("\n--- [InvoiceIQ RAG Answer] ---")
        print(answer)
        print("-----------------------------")
        return answer
    except Exception as e:
        print("\n--- [InvoiceIQ RAG Error] ---")
        print(f"Failed to generate RAG answer: {e}")
        return "Failed to generate RAG answer"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_question = " ".join(sys.argv[1:])
    else:
        print("--- InvoiceIQ RAG Query Mode ---")
        user_question = input("Enter a question about invoices or vendors: ").strip()

    if not user_question:
        print("Error: No question provided.")
        print("Example: python scripts/test_rag.py \"What was the total amount for INV-1002?\"")
        sys.exit(1)

    run_rag_query(user_question)
