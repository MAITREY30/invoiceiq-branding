import os
import sys
import json
from pprint import pprint

# --- Add project root to path ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------

try:
    from logic.extraction_agent import extract_invoice_data
    from logic.translation_agent import translate_invoice_data
    from src.utils.file_utils import read_metadata_file
    from config.settings import INCOMING_DIR
except ImportError as e:
    print(f"Error: Could not import modules in test_extraction.py: {e}")
    print("Please ensure __init__.py files exist and paths are correct.")
    sys.exit(1)

TEST_INVOICE_FILENAME = "INV_DE_004.pdf"
DEFAULT_LANGUAGE_CODE = "en"
VALID_EXTENSIONS = ('.pdf', '.png', '.jpg', '.jpeg')


def find_test_invoice() -> str:
    candidate_path = os.path.join(INCOMING_DIR, TEST_INVOICE_FILENAME)
    if os.path.exists(candidate_path):
        return candidate_path

    if not os.path.isdir(INCOMING_DIR):
        return ""

    for filename in sorted(os.listdir(INCOMING_DIR)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in VALID_EXTENSIONS:
            return os.path.join(INCOMING_DIR, filename)

    return ""


def test_extraction_pipeline():
    """Runs a demo extraction and translation test on an invoice."""
    print("--- InvoiceIQ Extraction Demo ---")

    test_filepath = find_test_invoice()
    if not test_filepath:
        print("Error: No valid invoice found in the incoming directory.")
        print(f"Please add a supported invoice file to: {INCOMING_DIR}")
        return

    print(f"Using invoice file: {test_filepath}")

    extracted_data = extract_invoice_data(test_filepath)
    if "error" in extracted_data:
        print("\n--- EXTRACTION FAILED ---")
        pprint(extracted_data)
        return

    print("\n--- EXTRACTION SUCCESSFUL ---")
    pprint(extracted_data)

    metadata = read_metadata_file(test_filepath) if os.path.exists(test_filepath) else {}
    language = metadata.get("language") or DEFAULT_LANGUAGE_CODE

    print("\n--- Starting Translation Demo ---")
    translated_data = translate_invoice_data(extracted_data, language_code=language)

    print("\n--- TRANSLATION COMPLETE ---")
    pprint(translated_data)

    output_filename = os.path.join(project_root, "invoiceiq_test_output.json")
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, indent=2, ensure_ascii=False)

    print(f"\n--- Demo output saved to: {output_filename} ---")


if __name__ == "__main__":
    test_extraction_pipeline()
