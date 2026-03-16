from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON,
    create_engine
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import datetime, timezone

from app.config import settings

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False)
    s3_key = Column(String(500), nullable=True)
    local_path = Column(String(500), nullable=True)
    total_pages = Column(Integer, default=0)
    status = Column(String(50), default="uploaded")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pages = relationship("Page", back_populates="document", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    ocr_text = Column(Text, default="")
    processed = Column(Boolean, default=False)

    document = relationship("Document", back_populates="pages")
    extractions = relationship("Extraction", back_populates="page", cascade="all, delete-orphan")


class ClauseCategory(Base):
    __tablename__ = "clause_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    color_hex = Column(String(7), default="#FFFF00")
    keywords = Column(JSON, default=list)

    extractions = relationship("Extraction", back_populates="category")


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("clause_categories.id"), nullable=False)
    extracted_text = Column(Text, default="")
    structured_data = Column(JSON, default=dict)
    confidence_score = Column(Float, default=0.0)
    source = Column(String(20), default="rule")
    needs_review = Column(Boolean, default=False)
    bbox_coordinates = Column(JSON, default=list)

    page = relationship("Page", back_populates="extractions")
    category = relationship("ClauseCategory", back_populates="extractions")
    review = relationship("ReviewItem", back_populates="extraction", uselist=False, cascade="all, delete-orphan")


class ReviewItem(Base):
    __tablename__ = "review_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    extraction_id = Column(Integer, ForeignKey("extractions.id"), nullable=False)
    status = Column(String(20), default="pending")
    reviewer_role = Column(String(50), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    extraction = relationship("Extraction", back_populates="review")


# Database setup
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    defaults = [
        {"name": "Medical", "color_hex": "#3B82F6", "keywords": [
            "medical", "patient", "diagnosis", "treatment", "clinical",
            "hospital", "doctor", "physician", "prescription", "therapy", "disease",
            "symptom", "healthcare", "insurance claim", "copay", "deductible",
            "pre-existing", "medication", "surgical", "chronic", "acute",
            "radiology", "pathology", "oncology", "cardiology", "pharmacy"
        ]},
        {"name": "Finance", "color_hex": "#10B981", "keywords": [
            "financial statement", "investment portfolio", "revenue", "profit margin",
            "budget allocation", "tax return", "interest rate", "loan", "mortgage", "equity fund",
            "dividend", "portfolio", "balance sheet", "cash flow", "fiscal year",
            "monetary policy", "capital gains", "credit score", "stock market",
            "mutual fund", "hedge fund", "bond yield", "financial audit"
        ]},
        {"name": "Sports", "color_hex": "#F59E0B", "keywords": [
            "sports", "athlete", "tournament", "championship", "league game",
            "player", "coach", "fitness", "stadium", "referee", "goalkeeper",
            "soccer", "basketball", "football game", "cricket", "tennis",
            "olympic", "marathon", "wrestling", "boxing", "batting average",
            "sports league", "world cup", "sports team", "playoff"
        ]},
    ]
    for cat_data in defaults:
        existing = db.query(ClauseCategory).filter_by(name=cat_data["name"]).first()
        if not existing:
            db.add(ClauseCategory(**cat_data))
        else:
            # Update keywords if category already exists
            existing.keywords = cat_data["keywords"]
    db.commit()
    db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
