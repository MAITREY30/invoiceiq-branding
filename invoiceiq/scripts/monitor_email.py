import imaplib
import email
from email.header import decode_header
import time
import os
from pathlib import Path

APP_NAME = "InvoiceIQ Email Monitor"
INCOMING_DIR = os.getenv("INCOMING_DIR", "data/incoming")
EMAIL_HOST = os.getenv("EMAIL_HOST", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER", "abc@gmail.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "abcd efgh ijkl mnop")
EMAIL_CHECK_INTERVAL = int(os.getenv("EMAIL_CHECK_INTERVAL", 10))
VALID_EXTENSIONS = ('.pdf', '.docx', '.png', '.jpg', '.jpeg')


def _normalize_incoming_dir(p) -> Path:
    path = Path(p).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_attachment(part, filename, incoming_path):
    filepath = os.path.join(incoming_path, filename)
    with open(filepath, "wb") as f:
        f.write(part.get_payload(decode=True))
    print(f"📎 Saved attachment: {filename}")


def process_incoming_emails():
    incoming_path = _normalize_incoming_dir(INCOMING_DIR)
    print(f"📨 {APP_NAME} started. Checking every {EMAIL_CHECK_INTERVAL}s")

    processed_uids = set()
    saved_files = set()

    try:
        mail = imaplib.IMAP4_SSL(EMAIL_HOST)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, data = mail.uid("search", None, "ALL")
        if status == "OK" and data and data[0]:
            processed_uids = {int(x) for x in data[0].split()}
        print(f"✅ Ignoring {len(processed_uids)} existing emails.")

        while True:
            try:
                status, data = mail.uid("search", None, "ALL")
                if status != "OK" or not data or not data[0]:
                    time.sleep(EMAIL_CHECK_INTERVAL)
                    continue

                current_uids = {int(x) for x in data[0].split()}
                new_uids = sorted(current_uids - processed_uids)

                if new_uids:
                    print(f"\n📬 Found {len(new_uids)} new email(s)")
                    for uid in new_uids:
                        status, msg_data = mail.uid("fetch", str(uid), "(RFC822)")
                        if status != "OK" or not msg_data or not msg_data[0]:
                            continue

                        msg = email.message_from_bytes(msg_data[0][1])
                        raw_subject = msg.get("Subject", "")
                        subject, encoding = decode_header(raw_subject)[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8", errors="ignore")
                        subject_lower = subject.lower().strip() if subject else ""

                        if "invoice" not in subject_lower:
                            print(f"⏩ Skipped (subject not invoice): {subject}")
                            processed_uids.add(uid)
                            continue

                        print(f"📩 New Invoice Email: {subject}")

                        for part in msg.walk():
                            if part.get_content_disposition() == "attachment":
                                filename = part.get_filename()
                                if not filename:
                                    continue
                                ext = os.path.splitext(filename)[1].lower()
                                if ext not in VALID_EXTENSIONS:
                                    continue

                                target = os.path.join(incoming_path, filename)
                                if filename in saved_files or os.path.exists(target):
                                    print(f"🔁 Already saved, skipping: {filename}")
                                    continue

                                save_attachment(part, filename, incoming_path)
                                saved_files.add(filename)

                        processed_uids.add(uid)

                time.sleep(EMAIL_CHECK_INTERVAL)

            except imaplib.IMAP4.abort:
                print("⚠️ Connection lost. Reconnecting...")
                time.sleep(5)
                mail = imaplib.IMAP4_SSL(EMAIL_HOST)
                mail.login(EMAIL_USER, EMAIL_PASS)
                mail.select("inbox")

            except Exception as e:
                print(f"[EmailMonitor] Error: {e}")
                time.sleep(5)

    except Exception as e:
        print(f"❌ Could not connect to mailbox: {e}")


if __name__ == "__main__":
    process_incoming_emails()
