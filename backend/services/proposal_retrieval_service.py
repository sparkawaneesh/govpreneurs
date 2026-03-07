import logging
from typing import List, Dict, Any
from rag.vector_service import VectorService
from services.experience_matching_service import ExperienceMatchingService

# Setup logging
logger = logging.getLogger(__name__)

class ProposalRetrievalService:
    """
    Service to collect RFP and company context for proposal generation.
    """

    def __init__(self):
        # RFP Vector Service (uses govpreneurs-rfps index by default)
        self.rfp_vector_service = VectorService()
        self.experience_matching_service = ExperienceMatchingService()

    def retrieve_context(self, opportunity_id: str, company_id: str) -> Dict[str, Any]:
        """
        Retrieves top RFP chunks and matching company experience.
        """
        logger.info(f"Retrieving context for Opportunity: {opportunity_id}, Company: {company_id}")

        try:
            # 1. Retrieve top 10 RFP chunks
            # Using a generic query to find the most relevant chunks if no specific query is provided.
            # In a real scenario, this might be "Technical Requirements" or similar.
            rfp_chunks = self.rfp_vector_service.similarity_search(
                query="Requirements and Scope of Work", 
                opportunity_id=opportunity_id,
                k=10
            )
            
            logger.info(f"Retrieved {len(rfp_chunks)} RFP chunks.")

            # 2. Combine RFP chunks to form a query for experience matching
            combined_rfp_text = " ".join([chunk["text"] for chunk in rfp_chunks])
            
            # 3. Retrieve matching company experience
            experience_data = self.experience_matching_service.match_experience(
                query=combined_rfp_text[:2000], # Limit query length for stability
                company_id=company_id,
                top_k=5
            )

            company_context = experience_data.get("matches", [])
            logger.info(f"Retrieved {len(company_context)} experience matches.")

            return {
                "rfp_context": rfp_chunks,
                "company_context": company_context
            }

        except Exception as e:
            logger.error(f"Failed to retrieve context: {str(e)}")
            raise
