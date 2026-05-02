import os
import sys
from pprint import pprint

# --- Add project root to path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------

try:
    from src.graph.workflow import graph_app
    from config.settings import INCOMING_DIR, PROCESSED_DIR, REVIEW_DIR
except ImportError as e:
    print(f"Error: Could not import modules in test_workflow.py: {e}")
    sys.exit(1)

DEFAULT_TEST_INVOICE = "INV_ES_003.pdf"
VALID_EXTENSIONS = ('.pdf', '.png', '.jpg', '.jpeg')


def locate_test_invoice(invoice_name: str = "") -> str:
    if invoice_name:
        custom_path = os.path.join(INCOMING_DIR, invoice_name)
        if os.path.exists(custom_path):
            return custom_path
        return ""

    for filename in sorted(os.listdir(INCOMING_DIR)):
        if os.path.splitext(filename)[1].lower() in VALID_EXTENSIONS:
            return os.path.join(INCOMING_DIR, filename)
    return ""


def run_workflow_test(invoice_filename: str = ""):
    print("--- InvoiceIQ Workflow Demo ---")

    selected_invoice = locate_test_invoice(invoice_filename or DEFAULT_TEST_INVOICE)
    if not selected_invoice:
        print("Error: No invoice file found in the incoming directory.")
        print(f"Please add a valid invoice to: {INCOMING_DIR}")
        available = [f for f in sorted(os.listdir(INCOMING_DIR)) if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS]
        if available:
            print("Available invoice candidates:")
            for f in available:
                print(f" - {f}")
        return

    print(f"Using invoice file: {selected_invoice}")

    metadata_path = os.path.splitext(selected_invoice)[0] + ".meta.json"
    if os.path.exists(metadata_path):
        print(f"Found metadata file: {metadata_path}")
    else:
        print(f"Warning: Metadata file not found at {metadata_path}")
        print("The workflow may run without a language hint.")

    print("Invoking InvoiceIQ workflow graph...")
    inputs = {"filepath": selected_invoice}

    try:
        final_state = graph_app.invoke(inputs)
        print("\n--- Workflow Execution Complete ---")
        print("\n--- Final State ---")
        pprint(final_state)

        print("\n--- Test Summary ---")
        if final_state.get("error"):
            print("RESULT: FAILED (Graph Error)")
            print(f"Error: {final_state['error']}")
        elif final_state.get("validation_status") == "PASSED":
            print("RESULT: SUCCESS (Validation Passed)")
            print(f"Processed invoice moved to: {PROCESSED_DIR}")
            print(f"Report JSON: {final_state.get('report_paths', {}).get('json')}")
            print(f"Indexed for RAG: {final_state.get('is_indexed')}")
        elif final_state.get("validation_status") == "FAILED":
            print("RESULT: SUCCESS (Validation Failed)")
            print(f"Invoice moved to review queue: {REVIEW_DIR}")
            print("Failed validation rules:")
            pprint([r for r in final_state.get('rules_results', []) if r.get('status') == 'FAILED'])
        else:
            print("RESULT: UNKNOWN")
            print("The graph completed but returned an inconclusive final state.")

    except Exception as e:
        print(f"\n--- CRITICAL ERROR during graph.invoke(): {e} ---")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    invoice_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    run_workflow_test(invoice_arg)

