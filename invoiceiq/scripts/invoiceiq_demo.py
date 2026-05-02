import os
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

SCRIPTS_DIR = project_root / "scripts"
DEMO_SCRIPTS = {
    "extraction": "test_extraction.py",
    "rag": "test_rag.py",
    "workflow": "test_workflow.py",
    "erp": "start_erp.py",
    "email": "monitor_email.py",
    "watcher": "temp_monitor.py",
}


def print_banner() -> None:
    print("""
========================================
InvoiceIQ Demo Launcher
========================================
This helper script starts common InvoiceIQ workflows and developer utilities.
""")


def print_help() -> None:
    print_banner()
    print("Usage:")
    print("  python scripts/invoiceiq_demo.py <command>")
    print("")
    print("Available commands:")
    for command in DEMO_SCRIPTS:
        print(f"  - {command}")
    print("")
    print("Examples:")
    print("  python scripts/invoiceiq_demo.py extraction")
    print("  python scripts/invoiceiq_demo.py rag")
    print("  python scripts/invoiceiq_demo.py workflow")
    print("  python scripts/invoiceiq_demo.py erp")
    print("  python scripts/invoiceiq_demo.py email")
    print("  python scripts/invoiceiq_demo.py watcher")


def run_script(script_name: str, extra_args: list[str] | None = None) -> int:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return 1

    command = [sys.executable, str(script_path)]
    if extra_args:
        command.extend(extra_args)

    print(f"\n--- Running InvoiceIQ helper: {script_name} ---")
    print("Command:", " ".join(command))
    return subprocess.run(command, cwd=str(project_root)).returncode


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help", "help"}:
        print_help()
        return 0

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command not in DEMO_SCRIPTS:
        print(f"Unknown command: {command}\n")
        print_help()
        return 1

    return run_script(DEMO_SCRIPTS[command], args)


if __name__ == "__main__":
    raise SystemExit(main())
