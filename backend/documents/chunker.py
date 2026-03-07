import uuid
import logging
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Setup logging
logger = logging.getLogger(__name__)

class DocumentChunker:
    """
    Service to split extracted document text into semantic chunks for RAG.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_document(self, pages: List[Dict[str, Any]], opportunity_id: str) -> List[Dict[str, Any]]:
        """
        Chunks text from a list of pages and returns structured chunks with metadata.
        """
        if not pages:
            logger.warning(f"No pages provided for chunking for opportunity {opportunity_id}")
            return []

        # Combine page texts into a single document while tracking page offsets
        combined_text = ""
        page_mappings = [] # List of (start_idx, end_idx, page_num)
        
        for p in pages:
            start_idx = len(combined_text)
            combined_text += p.get("text", "") + "\n\n"
            end_idx = len(combined_text)
            page_mappings.append((start_idx, end_idx, p.get("page")))

        doc_size = len(combined_text)
        logger.info(f"Chunking document for {opportunity_id}. Size: {doc_size} characters.")

        if doc_size == 0:
            return []

        # Use LangChain to split text
        # Note: split_text returns a list of strings. 
        # To get more granular metadata, we find the index of each chunk in the combined text.
        raw_chunks = self.text_splitter.split_text(combined_text)
        
        structured_chunks = []
        last_found_idx = 0
        
        for chunk_text in raw_chunks:
            # Find the index of this chunk in the combined text to determine page range
            # We search from last_found_idx to handle overlapping chunks correctly
            start_pos = combined_text.find(chunk_text, last_found_idx)
            if start_pos == -1:
                # Fallback if find fails for some reason (should not happen with standard splitting)
                start_pos = last_found_idx 
            
            end_pos = start_pos + len(chunk_text)
            last_found_idx = start_pos + 1 # Increment for next overlap search

            # Determine page ranges for this chunk
            page_start = None
            page_end = None
            
            for m_start, m_end, p_num in page_mappings:
                # If the chunk overlaps with this page's range
                if start_pos < m_end and end_pos > m_start:
                    if page_start is None:
                        page_start = p_num
                    page_end = p_num

            structured_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": chunk_text,
                "metadata": {
                    "page_start": page_start,
                    "page_end": page_end,
                    "opportunity_id": opportunity_id
                }
            })

        logger.info(f"Created {len(structured_chunks)} chunks for opportunity {opportunity_id}")
        return structured_chunks
