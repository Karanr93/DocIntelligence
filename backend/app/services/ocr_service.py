"""OCR Service using PyMuPDF (fitz) for text extraction and Tesseract for scanned images."""
from typing import List, Dict, Optional
import fitz  # PyMuPDF
import io
import os


class OCRService:
    """Handles PDF text extraction with fallback to Tesseract OCR for scanned pages."""

    def __init__(self, tesseract_path: Optional[str] = None):
        self._tesseract_available = False
        try:
            import pytesseract
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            elif os.name == "nt":
                default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                if os.path.exists(default):
                    pytesseract.pytesseract.tesseract_cmd = default
            self._tesseract_available = True
        except ImportError:
            pass

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from each page of a PDF.
        Returns list of {page_number, text, method, word_bboxes}.
        """
        doc = fitz.open(pdf_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            # Get word-level bounding boxes for highlighting
            word_bboxes = []
            words = page.get_text("words")
            for w in words:
                word_bboxes.append({
                    "x0": w[0], "y0": w[1], "x1": w[2], "y1": w[3],
                    "word": w[4]
                })

            method = "pymupdf"

            # If very little text extracted, fall back to Tesseract OCR
            if len(text.strip()) < 50 and self._tesseract_available:
                try:
                    import pytesseract
                    from PIL import Image
                    pix = page.get_pixmap(dpi=300)
                    img_bytes = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_bytes))
                    text = pytesseract.image_to_string(img)

                    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                    word_bboxes = []
                    for i in range(len(ocr_data["text"])):
                        if ocr_data["text"][i].strip():
                            word_bboxes.append({
                                "x0": ocr_data["left"][i],
                                "y0": ocr_data["top"][i],
                                "x1": ocr_data["left"][i] + ocr_data["width"][i],
                                "y1": ocr_data["top"][i] + ocr_data["height"][i],
                                "word": ocr_data["text"][i]
                            })
                    method = "tesseract"
                except Exception as e:
                    print(f"Tesseract OCR failed for page {page_num + 1}: {e}")

            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "method": method,
                "word_bboxes": word_bboxes
            })

        doc.close()
        return pages

    def get_page_dimensions(self, pdf_path: str, page_number: int) -> Dict:
        """Get the dimensions of a specific page."""
        doc = fitz.open(pdf_path)
        page = doc[page_number - 1]
        rect = page.rect
        doc.close()
        return {"width": rect.width, "height": rect.height}


ocr_service = OCRService()
