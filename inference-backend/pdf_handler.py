"""
PDF handling utilities.
"""

import importlib
from typing import Optional

def load_pdf_reader_class():
    """Load PDF reader class (pypdf or PyPDF2)."""
    for module_name in ["pypdf", "PyPDF2"]:
        try:
            module = importlib.import_module(module_name)
            return getattr(module, "PdfReader")
        except Exception:
            continue
    raise ImportError("Neither pypdf nor PyPDF2 is installed.")


def extract_text_from_pdf(pdf_path: str, max_chars_per_page: int = 1500) -> dict:
    """
    Extract text from all pages of a PDF.
    
    Returns:
        dict with page_number -> text mapping
    """
    try:
        PdfReader = load_pdf_reader_class()
        pdf_reader = PdfReader(pdf_path)
        
        texts = {}
        for i, page in enumerate(pdf_reader.pages):
            text = (page.extract_text() or "").strip()
            if not text:
                text = f"[No extractable text on page {i+1}]"
            texts[i + 1] = text[:max_chars_per_page]
        
        return texts
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")
