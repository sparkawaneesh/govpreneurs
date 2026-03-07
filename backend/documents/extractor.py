import fitz  # PyMuPDF
import logging
import re
from typing import List, Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

class PDFTextExtractor:
    """
    Service to extract and clean text from PDF documents using PyMuPDF.
    """

    def extract_text(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from a PDF file page by page.
        Returns a list of dictionaries containing page number and cleaned text.
        """
        logger.info(f"Starting text extraction for file: {pdf_path}")
        
        pages_content = []
        
        try:
            # Open the PDF document
            with fitz.open(pdf_path) as doc:
                num_pages = len(doc)
                logger.info(f"Processing {num_pages} pages for {pdf_path}")
                
                for page_num in range(num_pages):
                    page = doc.load_page(page_num)
                    raw_text = page.get_text("text")
                    
                    # Clean the extracted text
                    cleaned_text = self._clean_text(raw_text)
                    
                    if cleaned_text:
                        pages_content.append({
                            "page": page_num + 1,
                            "text": cleaned_text
                        })
                    else:
                        logger.warning(f"Empty or unextractable text on page {page_num + 1} of {pdf_path}")

            logger.info(f"Successfully extracted text from {len(pages_content)} pages.")
            return pages_content

        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            # Depending on requirements, we might want to raise or return partial results
            # For now, we return what we have or an empty list if it failed early
            return pages_content

    def _clean_text(self, text: str) -> str:
        """
        Cleans extracted text by normalizing whitespace and line breaks.
        """
        if not text:
            return ""

        # Remove excessive whitespace and normalize line breaks
        # 1. Replace multiple spaces with a single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 2. Normalize line breaks (replace multiple newlines with a double newline for paragraph separation)
        text = re.sub(r'(\r\n|\r|\n){2,}', '\n\n', text)
        
        # 3. Strip leading/trailing whitespace from each line and join
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text.strip()
