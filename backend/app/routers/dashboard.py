"""Dashboard routes for stats, charts, and filtering."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models import Document, Page, Extraction, ClauseCategory, get_db
from app.schemas import DashboardStats, DocumentListItem

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get overall dashboard statistics."""
    total = db.query(Document).count()
    completed = db.query(Document).filter_by(status="completed").count()
    pending = db.query(Document).filter(
        Document.status.in_(["uploaded", "processing"])
    ).count()
    failed = db.query(Document).filter_by(status="failed").count()

    # Clause counts: total extractions per category
    clause_counts = {}
    clause_doc_counts = {}
    categories = db.query(ClauseCategory).all()

    for cat in categories:
        # Total extraction count
        count = db.query(Extraction).filter_by(category_id=cat.id).count()
        clause_counts[cat.name] = count

        # Unique document count per category
        doc_count = (
            db.query(distinct(Page.document_id))
            .join(Extraction, Extraction.page_id == Page.id)
            .filter(Extraction.category_id == cat.id)
            .count()
        )
        clause_doc_counts[cat.name] = doc_count

    return DashboardStats(
        total_documents=total,
        processed_documents=completed,
        pending_documents=pending,
        failed_documents=failed,
        clause_counts=clause_counts,
        clause_document_counts=clause_doc_counts
    )


@router.get("/documents-by-clause", response_model=List[DocumentListItem])
def get_documents_by_clause(
    category: str = Query(..., description="Clause category name"),
    search: str = Query(None, description="Search within documents"),
    db: Session = Depends(get_db)
):
    """Get documents that contain a specific clause category."""
    cat = db.query(ClauseCategory).filter_by(name=category).first()
    if not cat:
        return []

    # Find all documents with extractions in this category
    doc_ids = (
        db.query(distinct(Page.document_id))
        .join(Extraction, Extraction.page_id == Page.id)
        .filter(Extraction.category_id == cat.id)
        .all()
    )
    doc_ids = [d[0] for d in doc_ids]

    results = []
    for doc_id in doc_ids:
        doc = db.query(Document).filter_by(id=doc_id).first()
        if not doc:
            continue

        # Apply search filter
        if search:
            search_lower = search.lower()
            if search_lower not in doc.filename.lower():
                pages = db.query(Page).filter_by(document_id=doc.id).all()
                found = any(search_lower in p.ocr_text.lower() for p in pages)
                if not found:
                    continue

        # Get relevant pages for this category
        relevant_pages = (
            db.query(distinct(Page.page_number))
            .join(Extraction, Extraction.page_id == Page.id)
            .filter(Page.document_id == doc_id, Extraction.category_id == cat.id)
            .all()
        )

        # Average confidence
        avg_conf = (
            db.query(func.avg(Extraction.confidence_score))
            .join(Page, Extraction.page_id == Page.id)
            .filter(Page.document_id == doc_id, Extraction.category_id == cat.id)
            .scalar()
        ) or 0.0

        results.append(DocumentListItem(
            id=doc.id,
            filename=doc.filename,
            total_pages=doc.total_pages,
            status=doc.status,
            relevance_pages=[p[0] for p in relevant_pages],
            confidence_avg=round(float(avg_conf), 2)
        ))

    return results


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all clause categories with their colors."""
    categories = db.query(ClauseCategory).all()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "color_hex": cat.color_hex,
            "keywords": cat.keywords
        }
        for cat in categories
    ]
