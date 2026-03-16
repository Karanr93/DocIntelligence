"""Sync all data (PDFs, OCR text, extractions, structured data) to S3."""
import os
import json
import boto3
from app.config import settings
from app.models import SessionLocal, Document, Page, Extraction, ClauseCategory

s3 = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)
BUCKET = settings.s3_bucket_name


def upload_text(key, content, content_type="application/json"):
    s3.put_object(Bucket=BUCKET, Key=key, Body=content, ContentType=content_type)


def upload_file(key, filepath):
    s3.upload_file(filepath, BUCKET, key)


def main():
    db = SessionLocal()

    # 1. Upload categories metadata
    print("Uploading clause categories...")
    categories = db.query(ClauseCategory).all()
    cat_data = []
    cat_lookup = {}
    for cat in categories:
        cat_dict = {
            "id": cat.id,
            "name": cat.name,
            "color_hex": cat.color_hex,
            "keywords": cat.keywords
        }
        cat_data.append(cat_dict)
        cat_lookup[cat.id] = cat.name
    upload_text("metadata/categories.json", json.dumps(cat_data, indent=2))
    print(f"  Uploaded {len(cat_data)} categories")

    # 2. Process each document
    documents = db.query(Document).all()
    doc_index = []

    for doc in documents:
        print(f"\nProcessing: {doc.filename} (id={doc.id})...")
        doc_prefix = f"documents/{doc.id}_{doc.filename.replace('.pdf', '')}"

        # 2a. Upload original PDF
        if doc.local_path and os.path.exists(doc.local_path):
            pdf_key = f"{doc_prefix}/original.pdf"
            upload_file(pdf_key, doc.local_path)
            print(f"  Uploaded PDF -> {pdf_key}")

        # 2b. Upload annotated PDF if exists
        annotated_path = os.path.join(settings.annotated_dir, f"annotated_{doc.id}_all.pdf")
        if os.path.exists(annotated_path):
            ann_key = f"{doc_prefix}/annotated_all.pdf"
            upload_file(ann_key, annotated_path)
            print(f"  Uploaded annotated PDF -> {ann_key}")

        # 2c. Upload OCR text per page
        pages = db.query(Page).filter_by(document_id=doc.id).order_by(Page.page_number).all()
        doc_ocr = {}

        for page in pages:
            # Individual page OCR
            page_key = f"{doc_prefix}/ocr/page_{page.page_number}.txt"
            upload_text(page_key, page.ocr_text, "text/plain")
            doc_ocr[f"page_{page.page_number}"] = page.ocr_text

        # Full document OCR combined
        full_ocr_key = f"{doc_prefix}/ocr/full_document_ocr.json"
        upload_text(full_ocr_key, json.dumps(doc_ocr, indent=2))
        print(f"  Uploaded OCR for {len(pages)} pages")

        # 2d. Upload extractions per page per category
        doc_extractions = {
            "document_id": doc.id,
            "filename": doc.filename,
            "total_pages": doc.total_pages,
            "status": doc.status,
            "categories": {}
        }

        for page in pages:
            extractions = db.query(Extraction).filter_by(page_id=page.id).all()

            for ext in extractions:
                cat_name = cat_lookup.get(ext.category_id, "Unknown")

                ext_data = {
                    "extraction_id": ext.id,
                    "page_number": page.page_number,
                    "category": cat_name,
                    "extracted_text": ext.extracted_text,
                    "structured_data": ext.structured_data,
                    "confidence_score": ext.confidence_score,
                    "source": ext.source,
                    "needs_review": ext.needs_review,
                    "bbox_coordinates": ext.bbox_coordinates
                }

                # Per-category per-page file
                ext_key = f"{doc_prefix}/extractions/{cat_name.lower()}/page_{page.page_number}.json"
                upload_text(ext_key, json.dumps(ext_data, indent=2))

                # Accumulate for summary
                if cat_name not in doc_extractions["categories"]:
                    doc_extractions["categories"][cat_name] = []
                doc_extractions["categories"][cat_name].append(ext_data)

        # 2e. Upload document-level extraction summary
        summary_key = f"{doc_prefix}/extraction_summary.json"
        upload_text(summary_key, json.dumps(doc_extractions, indent=2))
        print(f"  Uploaded extractions: {', '.join(f'{k}={len(v)}' for k, v in doc_extractions['categories'].items())}")

        # Build index entry
        doc_index.append({
            "id": doc.id,
            "filename": doc.filename,
            "total_pages": doc.total_pages,
            "status": doc.status,
            "s3_prefix": doc_prefix,
            "clause_summary": {k: len(v) for k, v in doc_extractions["categories"].items()}
        })

    # 3. Upload global index
    print("\nUploading global index...")
    upload_text("metadata/document_index.json", json.dumps(doc_index, indent=2))

    # 4. Upload dashboard summary
    dashboard = {
        "total_documents": len(documents),
        "processed": sum(1 for d in documents if d.status == "completed"),
        "clause_document_counts": {},
        "clause_extraction_counts": {}
    }
    for cat_name in cat_lookup.values():
        docs_with_cat = set()
        ext_count = 0
        for di in doc_index:
            if cat_name in di["clause_summary"]:
                docs_with_cat.add(di["id"])
                ext_count += di["clause_summary"][cat_name]
        dashboard["clause_document_counts"][cat_name] = len(docs_with_cat)
        dashboard["clause_extraction_counts"][cat_name] = ext_count
    upload_text("metadata/dashboard_summary.json", json.dumps(dashboard, indent=2))

    print(f"\n{'='*50}")
    print(f"SYNC COMPLETE!")
    print(f"Bucket: s3://{BUCKET}/")
    print(f"Documents: {len(documents)}")
    print(f"\nS3 Structure:")
    print(f"  s3://{BUCKET}/")
    print(f"    metadata/")
    print(f"      categories.json")
    print(f"      document_index.json")
    print(f"      dashboard_summary.json")
    print(f"    documents/")
    for di in doc_index:
        print(f"      {di['s3_prefix']}/")
        print(f"        original.pdf")
        print(f"        extraction_summary.json")
        print(f"        ocr/page_1.txt ... page_N.txt")
        print(f"        ocr/full_document_ocr.json")
        for cat in di["clause_summary"]:
            print(f"        extractions/{cat.lower()}/page_X.json")
        break  # Just show one example
    print(f"      ... ({len(doc_index)} documents total)")

    db.close()


if __name__ == "__main__":
    main()
