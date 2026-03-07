from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from models.database import get_db
from models.opportunity import Opportunity
from auth.auth_router import get_current_user
from middleware.rate_limiter import limiter

router = APIRouter(prefix="/opportunities", tags=["opportunities"])
recommendation_service = OpportunityRecommendationService()

@router.get("/recommend", response_model=OpportunityRecommendationResponse)
@limiter.limit("20/minute")
def recommend_opportunities(
    company_id: UUID,
    top_k: int = Query(10, ge=1, le=50),
    current_user: Any = Depends(get_current_user)
):
    """
    Recommend Sam.gov opportunities for a specific company based on their profile.
    """
    try:
        recommendations = recommendation_service.recommend_opportunities(company_id, top_k)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/", response_model=List[OpportunityRead])
def read_opportunities(
    limit: int = 20,
    offset: int = 0,
    naics_code: Optional[str] = None,
    agency: Optional[str] = None,
    set_aside_type: Optional[str] = None,
    deadline_before: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of opportunities with optional filters.
    """
    query = db.query(Opportunity)

    # Apply filters
    if naics_code:
        query = query.filter(Opportunity.naics_code == naics_code)
    if agency:
        query = query.filter(Opportunity.agency.ilike(f"%{agency}%"))
    if set_aside_type:
        query = query.filter(Opportunity.set_aside_type == set_aside_type)
    if deadline_before:
        query = query.filter(Opportunity.response_deadline <= deadline_before)

    # Ordering and pagination
    opportunities = query.order_by(desc(Opportunity.posted_date)).offset(offset).limit(limit).all()
    
    return opportunities

@router.get("/{id}", response_model=OpportunityDetail)
def read_opportunity(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single opportunity by its UUID.
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity
