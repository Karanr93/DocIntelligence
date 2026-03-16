"""Hybrid extraction pipeline: Rule-based -> LLM -> Human Review."""
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Document, Page, ClauseCategory, Extraction, ReviewItem
from app.services.ocr_service import ocr_service
from app.services.rule_engine import rule_engine
from app.services.llm_service import llm_service
from app.services.s3_service import s3_service


HIGH_CONFIDENCE = 0.85
LOW_CONFIDENCE = 0.50
RULE_ONLY_THRESHOLD = 0.80


class ExtractionPipeline:
    """Orchestrates the hybrid extraction: Rule -> LLM -> Review queue."""

    def process_document(self, document_id: int, db: Session) -> Dict:
        """Process a full document through the extraction pipeline."""
        document = db.query(Document).filter_by(id=document_id).first()
        if not document:
            return {"error": "Document not found"}

        document.status = "processing"
        db.commit()

        try:
            pdf_path = document.local_path
            ocr_results = ocr_service.extract_text_from_pdf(pdf_path)
            document.total_pages = len(ocr_results)

            for ocr_page in ocr_results:
                page = Page(
                    document_id=document.id,
                    page_number=ocr_page["page_number"],
                    ocr_text=ocr_page["text"]
                )
                db.add(page)
            db.commit()

            categories = db.query(ClauseCategory).all()
            pages = db.query(Page).filter_by(document_id=document.id).all()
            ocr_lookup = {p["page_number"]: p for p in ocr_results}

            stats = {"total_extractions": 0, "review_items": 0}

            for page in pages:
                ocr_data = ocr_lookup.get(page.page_number, {})
                word_bboxes = ocr_data.get("word_bboxes", [])

                for category in categories:
                    extraction_result = self._classify_page(
                        page.ocr_text, category, word_bboxes
                    )

                    if extraction_result["is_relevant"]:
                        extraction = Extraction(
                            page_id=page.id,
                            category_id=category.id,
                            extracted_text=extraction_result.get("extracted_text", ""),
                            structured_data=extraction_result.get("structured_data", {}),
                            confidence_score=extraction_result["confidence"],
                            source=extraction_result["source"],
                            needs_review=extraction_result["needs_review"],
                            bbox_coordinates=extraction_result.get("bboxes", [])
                        )
                        db.add(extraction)
                        db.flush()

                        stats["total_extractions"] += 1

                        if extraction_result["needs_review"]:
                            review = ReviewItem(
                                extraction_id=extraction.id,
                                status="pending"
                            )
                            db.add(review)
                            stats["review_items"] += 1

                page.processed = True

            document.status = "completed"
            db.commit()

            # Sync to S3 automatically
            try:
                self._sync_to_s3(document, pages, categories, db)
            except Exception as e:
                print(f"S3 sync failed (non-fatal): {e}")

            return {
                "document_id": document.id,
                "status": "completed",
                "total_pages": document.total_pages,
                **stats
            }

        except Exception as e:
            document.status = "failed"
            db.commit()
            return {"error": str(e), "document_id": document_id}

    def _classify_page(
        self, text: str, category: ClauseCategory, word_bboxes: List[Dict]
    ) -> Dict:
        """Hybrid classification: Rule -> LLM -> Review."""
        rule_result = rule_engine.classify_text(text, category.keywords, category.name)

        if not rule_result["matched"]:
            return {"is_relevant": False, "confidence": 0.0, "source": "rule", "needs_review": False}

        # If rule engine is very confident, skip LLM
        if rule_result["confidence"] >= RULE_ONLY_THRESHOLD:
            keyword_bboxes = rule_engine.find_keyword_bboxes(word_bboxes, rule_result["unique_keywords"])
            return {
                "is_relevant": True,
                "confidence": rule_result["confidence"],
                "source": "rule",
                "needs_review": False,
                "extracted_text": self._extract_relevant_sentences(text, rule_result["unique_keywords"]),
                "structured_data": {
                    "matched_keywords": rule_result["unique_keywords"],
                    "match_count": rule_result["total_matches"]
                },
                "bboxes": keyword_bboxes
            }

        # LLM for medium-confidence cases
        llm_result = llm_service.extract_clause(text, category.name)

        if not llm_result.get("is_relevant", False):
            return {"is_relevant": False, "confidence": 0.0, "source": "llm", "needs_review": False}

        combined_confidence = (rule_result["confidence"] * 0.3) + (llm_result.get("confidence", 0) * 0.7)

        structured_data = {
            "matched_keywords": rule_result["unique_keywords"],
            "llm_reasoning": llm_result.get("reasoning", ""),
            "sections": llm_result.get("extracted_sections", [])
        }

        extracted_text = "\n".join(
            s.get("text", "") for s in llm_result.get("extracted_sections", [])
        )

        keyword_bboxes = rule_engine.find_keyword_bboxes(word_bboxes, rule_result["unique_keywords"])
        needs_review = combined_confidence < LOW_CONFIDENCE

        return {
            "is_relevant": True,
            "confidence": round(combined_confidence, 2),
            "source": "llm",
            "needs_review": needs_review,
            "extracted_text": extracted_text or self._extract_relevant_sentences(text, rule_result["unique_keywords"]),
            "structured_data": structured_data,
            "bboxes": keyword_bboxes
        }

    def _sync_to_s3(self, document, pages, categories, db):
        """Sync processed document data to S3."""
        cat_lookup = {cat.id: cat.name for cat in categories}

        pages_data = [
            {"page_number": p.page_number, "ocr_text": p.ocr_text}
            for p in pages
        ]

        extractions_data = []
        for page in pages:
            exts = db.query(Extraction).filter_by(page_id=page.id).all()
            for ext in exts:
                extractions_data.append({
                    "page_number": page.page_number,
                    "category_name": cat_lookup.get(ext.category_id, "Unknown"),
                    "extracted_text": ext.extracted_text,
                    "structured_data": ext.structured_data,
                    "confidence_score": ext.confidence_score,
                    "source": ext.source,
                    "needs_review": ext.needs_review,
                    "bbox_coordinates": ext.bbox_coordinates
                })

        s3_service.sync_document_data(
            document_id=document.id,
            filename=document.filename,
            local_pdf_path=document.local_path,
            pages_data=pages_data,
            extractions_data=extractions_data,
            categories_lookup=cat_lookup
        )

    def _extract_relevant_sentences(self, text: str, keywords: List[str]) -> str:
        """Extract sentences containing any of the keywords."""
        sentences = text.replace("\n", " ").split(".")
        relevant = []
        kw_lower = {kw.lower() for kw in keywords}

        for sentence in sentences:
            sentence = sentence.strip()
            if any(kw in sentence.lower() for kw in kw_lower):
                relevant.append(sentence + ".")

        return " ".join(relevant[:10])


extraction_pipeline = ExtractionPipeline()
