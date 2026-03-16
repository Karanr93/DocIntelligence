from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime


class ClauseCategoryOut(BaseModel):
    id: int
    name: str
    color_hex: str
    keywords: List[str]

    class Config:
        orm_mode = True


class ExtractionOut(BaseModel):
    id: int
    page_id: int
    category_id: int
    category_name: str = ""
    extracted_text: str
    structured_data: dict
    confidence_score: float
    source: str
    needs_review: bool
    bbox_coordinates: list

    class Config:
        orm_mode = True


class PageOut(BaseModel):
    id: int
    page_number: int
    ocr_text: str
    processed: bool
    extractions: List[ExtractionOut] = []

    class Config:
        orm_mode = True


class DocumentOut(BaseModel):
    id: int
    filename: str
    total_pages: int
    status: str
    created_at: datetime
    clause_summary: Dict[str, int] = {}

    class Config:
        orm_mode = True


class DocumentDetail(DocumentOut):
    pages: List[PageOut] = []


class DashboardStats(BaseModel):
    total_documents: int
    processed_documents: int
    pending_documents: int
    failed_documents: int
    clause_counts: Dict[str, int]
    clause_document_counts: Dict[str, int]


class DocumentListItem(BaseModel):
    id: int
    filename: str
    total_pages: int
    status: str
    relevance_pages: List[int] = []
    confidence_avg: float = 0.0


class ReviewAction(BaseModel):
    status: str
    reviewer_role: str


class ReviewItemOut(BaseModel):
    id: int
    extraction_id: int
    status: str
    reviewer_role: Optional[str]
    extraction: ExtractionOut
    document_name: str = ""
    page_number: int = 0

    class Config:
        orm_mode = True
