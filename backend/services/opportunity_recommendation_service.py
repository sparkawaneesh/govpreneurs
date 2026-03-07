import logging
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.company_profile import CompanyProfile
from models.past_performance import PastPerformance
from models.opportunity import Opportunity
from rag.vector_service import VectorService
from cache.cache_service import CacheService
import os

logger = logging.getLogger(__name__)

class OpportunityRecommendationService:
    def __init__(self):
        self.vector_service = VectorService(index_name="rfp-chunks")
        self.cache = CacheService()

    def recommend_opportunities(self, company_id: UUID, top_k: int = 10) -> Dict[str, Any]:
        """
        Recommends Sam.gov opportunities based on company capabilities and past performance.
        """
        cache_key = f"recommend:{str(company_id)}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache HIT for recommendations: {company_id}")
            return cached_result

        logger.info(f"Generating recommendations for company: {company_id}")
        
        db = SessionLocal()
        try:
            # 1. Retrieve company profile and capabilities
            profile = db.query(CompanyProfile).filter(CompanyProfile.id == company_id).first()
            if not profile:
                logger.error(f"Company profile not found: {company_id}")
                return {"recommended_opportunities": []}

            past_performances = db.query(PastPerformance).filter(PastPerformance.company_id == company_id).all()

            # 2. Build semantic query
            query_parts = []
            if profile.capabilities_statement:
                query_parts.append(profile.capabilities_statement)
            if profile.core_services:
                query_parts.append(profile.core_services)
            
            for pp in past_performances:
                if pp.description:
                    query_parts.append(pp.description)
            
            semantic_query = " ".join(query_parts)
            
            if not semantic_query.strip():
                logger.warning("Empty semantic query for company profile.")
                return {"recommended_opportunities": []}

            # 3. Query Pinecone index (rfp-chunks)
            search_results = self.vector_service.similarity_search(semantic_query, k=50)

            # 4. Aggregate results by opportunity_id
            opportunity_scores = {}
            for res in search_results:
                opp_id = res.get("metadata", {}).get("opportunity_id")
                score = res.get("score", 0.0)
                if opp_id:
                    if opp_id not in opportunity_scores:
                        opportunity_scores[opp_id] = []
                    opportunity_scores[opp_id].append(score)

            # 5. Rank opportunities (average score for simplicity, or max)
            ranked_opps = []
            for opp_id_str, scores in opportunity_scores.items():
                avg_score = sum(scores) / len(scores)
                
                # Fetch opportunity details
                opp = db.query(Opportunity).filter(Opportunity.id == UUID(opp_id_str)).first()
                if opp:
                    ranked_opps.append({
                        "opportunity_id": str(opp.id),
                        "title": opp.title,
                        "agency": opp.agency,
                        "match_score": round(float(avg_score), 4)
                    })

            # Sort by score descending
            ranked_opps.sort(key=lambda x: x["match_score"], reverse=True)
            result = {
                "recommended_opportunities": ranked_opps[:top_k]
            }
            
            # Cache the result
            self.cache.set(cache_key, result, ttl=900)

            logger.info(f"Generated {len(ranked_opps[:top_k])} recommendations.")
            return result

        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            raise
        finally:
            db.close()
