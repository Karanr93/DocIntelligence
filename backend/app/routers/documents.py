"""Document upload and management routes."""
import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models import Document, Page, Extraction, ClauseCategory, get_db
from app.schemas import DocumentOut, DocumentDetail, ExtractionOut
from app.services.extraction import extraction_pipeline
from app.services.pdf_annotator import pdf_annotator
from app.services.s3_service import s3_service
from app.config import settings
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF document and start processing."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    # Save file locally
    local_path = os.path.join(settings.upload_dir, file.filename)
    with open(local_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create DB record
    document = Document(
        filename=file.filename,
        local_path=local_path,
        status="uploaded"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Upload to S3 in background
    s3_key = f"documents/{document.id}/{file.filename}"
    s3_path = s3_service.upload_file(local_path, s3_key)
    document.s3_key = s3_path
    db.commit()

    # Process in background
    background_tasks.add_task(_process_document, document.id)

    return _doc_to_response(document, db)


def _process_document(document_id: int):
    """Background task to process a document."""
    from app.models import SessionLocal
    db = SessionLocal()
    try:
        extraction_pipeline.process_document(document_id, db)
    finally:
        db.close()


@router.get("/", response_model=List[DocumentOut])
def list_documents(
    status: str = None,
    category: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """List all documents with optional filters."""
    query = db.query(Document)

    if status:
        query = query.filter(Document.status == status)

    documents = query.order_by(Document.created_at.desc()).all()

    results = []
    for doc in documents:
        doc_response = _doc_to_response(doc, db)

        # Filter by category
        if category and category not in doc_response.clause_summary:
            continue

        # Filter by search
        if search:
            search_lower = search.lower()
            if search_lower not in doc.filename.lower():
                # Check if search term exists in any extraction
                pages = db.query(Page).filter_by(document_id=doc.id).all()
                found = False
                for page in pages:
                    if search_lower in page.ocr_text.lower():
                        found = True
                        break
                if not found:
                    continue

        results.append(doc_response)

    return results


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, role: str = None, db: Session = Depends(get_db)):
    """Get document details with extractions, optionally filtered by role."""
    document = db.query(Document).filter_by(id=document_id).first()
    if not document:
        raise HTTPException(404, "Document not found")

    pages = db.query(Page).filter_by(document_id=document_id).order_by(Page.page_number).all()

    page_list = []
    for page in pages:
        ext_query = db.query(Extraction).filter_by(page_id=page.id)

        if role:
            cat = db.query(ClauseCategory).filter_by(name=role).first()
            if cat:
                ext_query = ext_query.filter_by(category_id=cat.id)

        extractions = ext_query.all()
        ext_list = []
        for ext in extractions:
            cat = db.query(ClauseCategory).filter_by(id=ext.category_id).first()
            ext_list.append(ExtractionOut(
                id=ext.id,
                page_id=ext.page_id,
                category_id=ext.category_id,
                category_name=cat.name if cat else "",
                extracted_text=ext.extracted_text,
                structured_data=ext.structured_data,
                confidence_score=ext.confidence_score,
                source=ext.source,
                needs_review=ext.needs_review,
                bbox_coordinates=ext.bbox_coordinates
            ))

        from app.schemas import PageOut
        page_list.append(PageOut(
            id=page.id,
            page_number=page.page_number,
            ocr_text=page.ocr_text,
            processed=page.processed,
            extractions=ext_list
        ))

    doc_response = _doc_to_response(document, db)
    return DocumentDetail(
        **doc_response.dict(),
        pages=page_list
    )


@router.get("/{document_id}/annotated")
def download_annotated_pdf(
    document_id: int,
    role: str = None,
    db: Session = Depends(get_db)
):
    """Download annotated PDF with highlights for a specific role."""
    document = db.query(Document).filter_by(id=document_id).first()
    if not document:
        raise HTTPException(404, "Document not found")

    try:
        output_path = pdf_annotator.create_annotated_pdf(document_id, db, role_filter=role)
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"annotated_{document.filename}"
        )
    except Exception as e:
        raise HTTPException(500, f"Failed to generate annotated PDF: {str(e)}")


@router.post("/{document_id}/reprocess")
def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reprocess a document (clears existing extractions)."""
    document = db.query(Document).filter_by(id=document_id).first()
    if not document:
        raise HTTPException(404, "Document not found")

    # Clear existing pages and extractions
    pages = db.query(Page).filter_by(document_id=document_id).all()
    for page in pages:
        db.query(Extraction).filter_by(page_id=page.id).delete()
    db.query(Page).filter_by(document_id=document_id).delete()

    document.status = "uploaded"
    db.commit()

    background_tasks.add_task(_process_document, document_id)
    return {"message": "Reprocessing started", "document_id": document_id}


def _doc_to_response(doc: Document, db: Session) -> DocumentOut:
    """Convert Document model to response with clause summary."""
    clause_summary = {}
    pages = db.query(Page).filter_by(document_id=doc.id).all()
    for page in pages:
        extractions = db.query(Extraction).filter_by(page_id=page.id).all()
        for ext in extractions:
            cat = db.query(ClauseCategory).filter_by(id=ext.category_id).first()
            if cat:
                clause_summary[cat.name] = clause_summary.get(cat.name, 0) + 1

    return DocumentOut(
        id=doc.id,
        filename=doc.filename,
        total_pages=doc.total_pages,
        status=doc.status,
        created_at=doc.created_at,
        clause_summary=clause_summary
    )
