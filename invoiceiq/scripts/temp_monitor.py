import time
import os
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

class InvoiceFileHandler(FileSystemEventHandler):
    """Handles file system events for invoice files."""

    def __init__(self, on_new_file: Optional[Callable[[str], None]] = None):
        self.on_new_file = on_new_file
        super().__init__()

    def on_created(self, event):
        if event.is_directory:
            return

        if isinstance(event, FileCreatedEvent):
            file_path = event.src_path
            print(f"InvoiceIQ detected new file: {file_path}")

            if self.on_new_file:
                try:
                    self.on_new_file(file_path)
                except Exception as e:
                    print(f"Error processing new invoice file {file_path}: {e}")


class InvoiceIQMonitor:
    """InvoiceIQ watcher that monitors the incoming directory for new invoices."""

    def __init__(self, inbox_path: str, on_new_file: Optional[Callable[[str], None]] = None):
        self.inbox_path = inbox_path
        self.on_new_file = on_new_file
        self._observer = None
        self._handler = None

    def start(self):
        Path(self.inbox_path).mkdir(parents=True, exist_ok=True)
        self._handler = InvoiceFileHandler(on_new_file=self.on_new_file)
        self._observer = Observer()
        self._observer.schedule(self._handler, self.inbox_path, recursive=False)
        self._observer.start()
        print(f"InvoiceIQ watcher started on: {self.inbox_path}")

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
            print("InvoiceIQ watcher stopped.")

    def run(self):
        try:
            self.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt received, shutting down watcher.")
        finally:
            self.stop()


if __name__ == "__main__":
    inbox_dir = os.getenv("INCOMING_DIR", "data/incoming")
    monitor = InvoiceIQMonitor(inbox_dir)
    monitor.run()
