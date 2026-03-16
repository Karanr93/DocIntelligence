"""Script to upload all sample PDFs to the running backend."""
import os
import sys
import time
import httpx

API_BASE = "http://localhost:8000/api"
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_pdfs")


def main():
    pdfs = [f for f in os.listdir(SAMPLE_DIR) if f.endswith(".pdf")]
    print(f"Found {len(pdfs)} sample PDFs to upload")

    for pdf_name in sorted(pdfs):
        pdf_path = os.path.join(SAMPLE_DIR, pdf_name)
        print(f"  Uploading: {pdf_name}...", end=" ")

        with open(pdf_path, "rb") as f:
            response = httpx.post(
                f"{API_BASE}/documents/upload",
                files={"file": (pdf_name, f, "application/pdf")},
                timeout=30.0
            )

        if response.status_code == 200:
            data = response.json()
            print(f"OK (id={data['id']}, status={data['status']})")
        else:
            print(f"FAILED ({response.status_code}: {response.text})")

    # Wait for processing
    print("\nWaiting for processing to complete...")
    for i in range(30):
        time.sleep(2)
        stats = httpx.get(f"{API_BASE}/dashboard/stats").json()
        total = stats["total_documents"]
        done = stats["processed_documents"]
        pending = stats["pending_documents"]
        failed = stats["failed_documents"]
        print(f"  Progress: {done}/{total} completed, {pending} pending, {failed} failed")

        if pending == 0:
            break

    # Show final stats
    print("\n--- Final Dashboard Stats ---")
    stats = httpx.get(f"{API_BASE}/dashboard/stats").json()
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Processed: {stats['processed_documents']}")
    print(f"Failed: {stats['failed_documents']}")
    print(f"Clause Counts: {stats['clause_counts']}")
    print(f"Documents per Clause: {stats['clause_document_counts']}")


if __name__ == "__main__":
    main()
