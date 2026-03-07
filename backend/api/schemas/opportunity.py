from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any

class OpportunityBase(BaseModel):
    title: Optional[str] = None
    agency: Optional[str] = None
    naics_code: Optional[str] = None
    set_aside_type: Optional[str] = None
    response_deadline: Optional[datetime] = None
    posted_date: Optional[datetime] = None

class OpportunityRead(OpportunityBase):
    id: UUID

    class Config:
        from_attributes = True

class OpportunityDetail(OpportunityRead):
    notice_id: str
    solicitation_number: Optional[str] = None
    department: Optional[str] = None
    naics_description: Optional[str] = None
    description: Optional[str] = None
    scope_of_work: Optional[str] = None
    place_of_performance_city: Optional[str] = None
    place_of_performance_state: Optional[str] = None
    place_of_performance_country: Optional[str] = None
    estimated_value: Optional[str] = None
    contract_type: Optional[str] = None
    attachments: Optional[List[Any]] = None
    keywords: Optional[List[str]] = None
    last_synced_at: datetime

class OpportunityRecommendation(BaseModel):
    opportunity_id: str
    title: str
    agency: str
    match_score: float

class OpportunityRecommendationResponse(BaseModel):
    recommended_opportunities: List[OpportunityRecommendation]
