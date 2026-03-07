import logging
from typing import List, Dict, Any
from vector.company_vector_service import CompanyVectorService

# Setup logging
logger = logging.getLogger(__name__)

class ExperienceMatchingService:
    """
    Service to match RFP requirements with company capabilities and past performance.
    """

    def __init__(self):
        self.vector_service = CompanyVectorService()

    def match_experience(self, query: str, company_id: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Finds the best matching capabilities and past performance for a given query.
        """
        logger.info(f"Executing experience match for company {company_id}. Query: {query}")
        
        try:
            matches = self.vector_service.similarity_search(
                query=query,
                company_id=company_id,
                k=top_k
            )

            formatted_matches = []
            for m in matches:
                metadata = m.get("metadata", {})
                formatted_matches.append({
                    "type": metadata.get("type", "unknown"),
                    "project_name": metadata.get("project_name", "N/A"),
                    "text": m.get("text"),
                    "score": m.get("score")
                })

            logger.info(f"Returned {len(formatted_matches)} matches for company {company_id}")
            
            return {
                "query": query,
                "matches": formatted_matches
            }

        except Exception as e:
            logger.error(f"Experience matching failed: {str(e)}")
            raise
