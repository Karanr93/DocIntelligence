"""Review queue routes for human-in-the-loop verification."""
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import ReviewItem, Extraction, Page, Document, ClauseCategory, get_db
from app.schemas import ReviewItemOut, ReviewAction, ExtractionOut

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/", response_model=List[ReviewItemOut])
def get_review_queue(
    status: str = "pending",
    role: str = None,
    db: Session = Depends(get_db)
):
    """Get review queue items, optionally filtered by status and role."""
    query = db.query(ReviewItem).filter_by(status=status)

    items = query.all()
    results = []

    for item in items:
        extraction = db.query(Extraction).filter_by(id=item.extraction_id).first()
        if not extraction:
            continue

        cat = db.query(ClauseCategory).filter_by(id=extraction.category_id).first()

        # Role filter
        if role and cat and cat.name != role:
            continue

        page = db.query(Page).filter_by(id=extraction.page_id).first()
        doc = db.query(Document).filter_by(id=page.document_id).first() if page else None

        ext_out = ExtractionOut(
            id=extraction.id,
            page_id=extraction.page_id,
            category_id=extraction.category_id,
            category_name=cat.name if cat else "",
            extracted_text=extraction.extracted_text,
            structured_data=extraction.structured_data,
            confidence_score=extraction.confidence_score,
            source=extraction.source,
            needs_review=extraction.needs_review,
            bbox_coordinates=extraction.bbox_coordinates
        )

        results.append(ReviewItemOut(
            id=item.id,
            extraction_id=item.extraction_id,
            status=item.status,
            reviewer_role=item.reviewer_role,
            extraction=ext_out,
            document_name=doc.filename if doc else "",
            page_number=page.page_number if page else 0
        ))

    return results


@router.put("/{review_id}")
def update_review(
    review_id: int,
    action: ReviewAction,
    db: Session = Depends(get_db)
):
    """Approve or reject a review item."""
    item = db.query(ReviewItem).filter_by(id=review_id).first()
    if not item:
        raise HTTPException(404, "Review item not found")

    item.status = action.status
    item.reviewer_role = action.reviewer_role
    item.reviewed_at = datetime.now(timezone.utc)

    # Update extraction
    extraction = db.query(Extraction).filter_by(id=item.extraction_id).first()
    if extraction:
        extraction.needs_review = False
        if action.status == "rejected":
            # Remove the extraction if rejected
            db.delete(extraction)
        else:
            extraction.source = "human"
            extraction.confidence_score = 1.0

    db.commit()

    return {"message": f"Review item {action.status}", "id": review_id}


@router.get("/stats")
def review_stats(db: Session = Depends(get_db)):
    """Get review queue statistics."""
    pending = db.query(ReviewItem).filter_by(status="pending").count()
    approved = db.query(ReviewItem).filter_by(status="approved").count()
    rejected = db.query(ReviewItem).filter_by(status="rejected").count()

    return {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "total": pending + approved + rejected
    }
