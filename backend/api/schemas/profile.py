from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any

# --- Past Performance Schemas ---

class PastPerformanceBase(BaseModel):
    project_name: str
    client: str
    description: Optional[str] = None
    contract_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PastPerformanceCreate(PastPerformanceBase):
    company_profile_id: UUID

class PastPerformanceRead(PastPerformanceBase):
    id: UUID
    company_profile_id: UUID

    class Config:
        from_attributes = True

# --- Company Profile Schemas ---

class CompanyProfileBase(BaseModel):
    company_name: str
    capabilities_statement: Optional[str] = None
    core_services: Optional[List[str]] = None
    naics_codes: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    team_size: Optional[str] = None
    location: Optional[str] = None

class CompanyProfileCreate(CompanyProfileBase):
    user_id: str

class CompanyProfileUpdate(CompanyProfileBase):
    company_name: Optional[str] = None

class CompanyProfileRead(CompanyProfileBase):
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    past_performances: List[PastPerformanceRead] = []

    class Config:
        from_attributes = True
