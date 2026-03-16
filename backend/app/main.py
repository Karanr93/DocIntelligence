"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import init_db
from app.routers import documents, dashboard, review

app = FastAPI(
    title="Document Clause Extraction System",
    description="POC for extracting and classifying Medical, Finance, and Sports clauses from PDF documents",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(dashboard.router)
app.include_router(review.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
