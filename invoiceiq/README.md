# InvoiceIQ Processing Suite

## Overview

InvoiceIQ is a modern invoice review and auditing platform that automates extraction, validation, and reporting for incoming invoices. It is built to support multi-currency operations, configurable validation policies, and ERP-ready workflows.

## Features

- **Automated Invoice Extraction:** Processes PDF, PNG, JPG invoices and extracts structured fields.
- **Smart Validation & Scoring:** Uses `config/rules.yaml` to enforce field requirements, tolerance rules, currency checks, and invoice health scoring.
- **Multi-Currency Support:** Maps currency symbols and validates against accepted currency lists.
- **Risk-Aware Reporting:** Generates HTML reports with discrepancy summaries, translation confidence, and invoice risk indicators.
- **Audit Logging:** Tracks actions and validation events for compliance and observability.

## Agents

The system is modular, with specialized agents handling different aspects of invoice processing:

### Extraction Agent (`src/logic/extraction_agent.py`)

- Extracts invoice data from PDF files using OCR and parsing techniques.
- Identifies header and line item fields as defined in `rules.yaml`.
- Handles multi-format invoices and normalizes extracted data.

### Validation Agent (`src/logic/validation_agent.py`)

- Validates extracted invoice data against rules in `rules.yaml`.
- Checks for missing fields, data type mismatches, currency validity, and total mismatches.
- Applies tolerances for rounding and price/quantity differences.
- Flags invoices for review or rejection based on validation policies.

### Translation Agent (`src/logic/translation_agent.py`)

- Translates invoice content to the required language if needed.
- Provides translation confidence scores for reporting.
- Ensures field values are consistent post-translation.

### Reporting Agent (`src/logic/reporting_agent.py`)

- Generates detailed HTML reports for each processed invoice.
- Includes translation confidence, discrepancy summaries, and validation results.
- Supports multiple report formats as configured in `rules.yaml`.

### RAG Agent (`src/rag/rag_agent.py`)

- Implements Retrieval-Augmented Generation for advanced document search and Q&A.
- Uses vector stores for semantic search over invoice and ERP data.
- Supports chatbot and review queue functionalities.

### Monitor Agent (`scripts/monitor_agent.py`)

- Monitors incoming invoices and triggers extraction and validation workflows.
- Tracks processing status and logs audit events.

## Project Structure

- `app.py`: Main application entry point.
- `config/`: Configuration files (`rules.yaml`, `settings.py`).
- `data/`: Incoming invoices, mock ERP data, and vector store.
- `pages/`: Streamlit UI pages for chatbot, review queue, monitoring, and invoice history.
- `reports/`: Generated reports (HTML, JSON, pending review).
- `scripts/`: Utility and test scripts.
- `src/`: Source code modules:
  - `erp/`: ERP integration and models.
  - `graph/`: Workflow logic.
  - `llm/`: LLM gateway integration.
  - `logic/`: Agents for extraction, validation, reporting, translation.
  - `models/`: Data models.
  - `rag/`: Retrieval-Augmented Generation components.
  - `utils/`: Utility functions.

## Configuration

All validation and processing rules are defined in `config/rules.yaml`, including:

- Required fields for header and line items
- Data types for each field
- Tolerances for financial calculations
- Accepted currencies and symbol mapping
- Validation policies for missing fields, mismatches, and invalid currencies
- Reporting and logging options

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```
2. **Configure settings:** Edit `config/settings.py` and `config/rules.yaml` as needed.
3. **Run the application:**
   ```bash
   python app.py
   ```
4. **Access the UI:** Open the Streamlit pages in your browser for chatbot, review, monitoring, and history.
5. **Run the InvoiceIQ demo launcher:**
   ```bash
   python scripts/invoiceiq_demo.py extraction
   ```

> Tip: The dashboard now includes an invoice health score, risk rating, and review efficiency indicator to highlight operations for stakeholders.

## Usage

- Place incoming invoices in `data/incoming_copy/`.
- Review processed invoices and reports in the `reports/` directory.
- Monitor workflow and validation status via the UI.
