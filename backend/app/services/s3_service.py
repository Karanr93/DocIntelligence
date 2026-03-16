"""S3 Service for PDF storage and data sync."""
import json
import boto3
import os
from app.config import settings


class S3Service:
    """Handles file uploads to S3. Falls back to local storage if AWS not configured."""

    def __init__(self):
        self.use_s3 = bool(settings.aws_access_key_id and settings.aws_secret_access_key)
        if self.use_s3:
            try:
                self.client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
                self.bucket = settings.s3_bucket_name
            except Exception:
                self.use_s3 = False

    def upload_file(self, local_path, s3_key):
        """Upload file to S3. Returns the S3 URI or local path."""
        if self.use_s3:
            try:
                self.client.upload_file(local_path, self.bucket, s3_key)
                return f"s3://{self.bucket}/{s3_key}"
            except Exception as e:
                print(f"S3 upload failed, using local: {e}")
        return local_path

    def upload_json(self, s3_key, data):
        """Upload a JSON object to S3."""
        if self.use_s3:
            try:
                self.client.put_object(
                    Bucket=self.bucket, Key=s3_key,
                    Body=json.dumps(data, indent=2),
                    ContentType="application/json"
                )
                return True
            except Exception as e:
                print(f"S3 JSON upload failed: {e}")
        return False

    def upload_text(self, s3_key, text):
        """Upload plain text to S3."""
        if self.use_s3:
            try:
                self.client.put_object(
                    Bucket=self.bucket, Key=s3_key,
                    Body=text, ContentType="text/plain"
                )
                return True
            except Exception as e:
                print(f"S3 text upload failed: {e}")
        return False

    def download_file(self, s3_key, local_path):
        """Download file from S3. Returns local path."""
        if self.use_s3 and s3_key.startswith("s3://"):
            try:
                key = s3_key.replace(f"s3://{self.bucket}/", "")
                self.client.download_file(self.bucket, key, local_path)
                return local_path
            except Exception as e:
                print(f"S3 download failed: {e}")
        return s3_key

    def sync_document_data(self, document_id, filename, local_pdf_path,
                           pages_data, extractions_data, categories_lookup):
        """
        Sync all data for a processed document to S3.
        Called automatically after document processing completes.

        pages_data: list of {page_number, ocr_text}
        extractions_data: list of {page_number, category_name, extracted_text,
                          structured_data, confidence_score, source, needs_review, bbox_coordinates}
        categories_lookup: dict {category_id: category_name}
        """
        if not self.use_s3:
            return

        doc_name = filename.replace('.pdf', '').replace(' ', '_')
        prefix = f"documents/{document_id}_{doc_name}"

        try:
            # 1. Upload original PDF
            if local_pdf_path and os.path.exists(local_pdf_path):
                self.upload_file(local_pdf_path, f"{prefix}/original.pdf")

            # 2. Upload OCR text per page
            doc_ocr = {}
            for page in pages_data:
                page_num = page["page_number"]
                self.upload_text(
                    f"{prefix}/ocr/page_{page_num}.txt",
                    page["ocr_text"]
                )
                doc_ocr[f"page_{page_num}"] = page["ocr_text"]

            # Full combined OCR
            self.upload_json(f"{prefix}/ocr/full_document_ocr.json", doc_ocr)

            # 3. Upload extractions per category per page
            doc_summary = {
                "document_id": document_id,
                "filename": filename,
                "total_pages": len(pages_data),
                "categories": {}
            }

            for ext in extractions_data:
                cat_name = ext["category_name"]
                page_num = ext["page_number"]

                ext_data = {
                    "page_number": page_num,
                    "category": cat_name,
                    "extracted_text": ext["extracted_text"],
                    "structured_data": ext["structured_data"],
                    "confidence_score": ext["confidence_score"],
                    "source": ext["source"],
                    "needs_review": ext["needs_review"],
                    "bbox_coordinates": ext["bbox_coordinates"]
                }

                self.upload_json(
                    f"{prefix}/extractions/{cat_name.lower()}/page_{page_num}.json",
                    ext_data
                )

                if cat_name not in doc_summary["categories"]:
                    doc_summary["categories"][cat_name] = []
                doc_summary["categories"][cat_name].append(ext_data)

            # 4. Upload document extraction summary
            self.upload_json(f"{prefix}/extraction_summary.json", doc_summary)

            # 5. Update global document index
            self._update_global_index(document_id, filename, len(pages_data), doc_summary)

            print(f"S3 sync complete for document {document_id}: {filename}")

        except Exception as e:
            print(f"S3 sync failed for document {document_id}: {e}")

    def _update_global_index(self, document_id, filename, total_pages, doc_summary):
        """Update the global document index in S3."""
        try:
            # Try to read existing index
            try:
                obj = self.client.get_object(
                    Bucket=self.bucket, Key="metadata/document_index.json"
                )
                index = json.loads(obj["Body"].read().decode())
            except Exception:
                index = []

            # Remove existing entry for this doc if re-processing
            index = [d for d in index if d.get("id") != document_id]

            # Add new entry
            index.append({
                "id": document_id,
                "filename": filename,
                "total_pages": total_pages,
                "status": "completed",
                "clause_summary": {
                    k: len(v) for k, v in doc_summary["categories"].items()
                }
            })

            self.upload_json("metadata/document_index.json", index)

        except Exception as e:
            print(f"Failed to update global index: {e}")


s3_service = S3Service()
