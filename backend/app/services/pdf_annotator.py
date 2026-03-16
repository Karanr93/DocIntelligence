"""PDF Annotator - Creates highlighted PDFs with color-coded clause annotations."""
import fitz  # PyMuPDF
import os
from sqlalchemy.orm import Session
from app.models import Document, Page, Extraction, ClauseCategory
from app.config import settings


class PDFAnnotator:
    """Creates annotated PDF copies with color-coded highlights per clause category."""

    # Default colors (RGB tuples, 0-1 range)
    COLOR_MAP = {
        "Medical": (0.23, 0.51, 0.96),    # #3B82F6 blue
        "Finance": (0.06, 0.73, 0.51),    # #10B981 green
        "Sports": (0.96, 0.62, 0.04),     # #F59E0B amber
    }

    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple (0-1 range)."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def create_annotated_pdf(
        self,
        document_id: int,
        db: Session,
        role_filter: str = None
    ) -> str:
        """
        Create an annotated PDF with highlights for a specific role.
        If role_filter is set, only highlight that category.
        Returns path to the annotated PDF.
        """
        document = db.query(Document).filter_by(id=document_id).first()
        if not document or not document.local_path:
            raise ValueError(f"Document {document_id} not found or no file path")

        doc = fitz.open(document.local_path)

        # Get all extractions for this document
        pages = db.query(Page).filter_by(document_id=document_id).all()

        for page_record in pages:
            query = db.query(Extraction).filter_by(page_id=page_record.id)

            if role_filter:
                category = db.query(ClauseCategory).filter_by(name=role_filter).first()
                if category:
                    query = query.filter_by(category_id=category.id)

            extractions = query.all()
            if not extractions:
                continue

            pdf_page = doc[page_record.page_number - 1]

            for extraction in extractions:
                cat = db.query(ClauseCategory).filter_by(id=extraction.category_id).first()
                color = self.hex_to_rgb(cat.color_hex) if cat else (1, 1, 0)

                # Method 1: Highlight using bbox coordinates if available
                if extraction.bbox_coordinates:
                    for bbox in extraction.bbox_coordinates:
                        if isinstance(bbox, dict):
                            rect = fitz.Rect(bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"])
                        elif isinstance(bbox, list) and len(bbox) == 4:
                            rect = fitz.Rect(bbox)
                        else:
                            continue
                        annot = pdf_page.add_highlight_annot(rect)
                        annot.set_colors(stroke=color)
                        annot.set_opacity(0.35)
                        annot.update()

                # Method 2: Search for extracted text and highlight
                elif extraction.extracted_text:
                    # Search for key phrases in the page
                    phrases = extraction.extracted_text.split(".")
                    for phrase in phrases[:5]:  # Limit to 5 phrases
                        phrase = phrase.strip()
                        if len(phrase) < 10:
                            continue
                        # Search first 100 chars of each phrase
                        search_text = phrase[:100]
                        instances = pdf_page.search_for(search_text)
                        for inst in instances:
                            annot = pdf_page.add_highlight_annot(inst)
                            annot.set_colors(stroke=color)
                            annot.set_opacity(0.35)
                            annot.update()

        # Save annotated PDF
        role_suffix = f"_{role_filter}" if role_filter else "_all"
        output_filename = f"annotated_{document.id}{role_suffix}.pdf"
        output_path = os.path.join(settings.annotated_dir, output_filename)

        doc.save(output_path)
        doc.close()

        return output_path

    def get_category_color(self, category_name: str) -> tuple:
        return self.COLOR_MAP.get(category_name, (1, 1, 0))


pdf_annotator = PDFAnnotator()
