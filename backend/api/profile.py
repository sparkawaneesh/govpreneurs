from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from models.database import get_db
from models.company_profile import CompanyProfile
from models.past_performance import PastPerformance
from api.schemas.profile import (
    CompanyProfileCreate, CompanyProfileUpdate, CompanyProfileRead,
    PastPerformanceCreate, PastPerformanceRead
)
from auth.auth_router import get_current_user

router = APIRouter(
    prefix="/profile", 
    tags=["profile"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=CompanyProfileRead)
def create_profile(profile: CompanyProfileCreate, db: Session = Depends(get_db)):
    """
    Create a new company profile.
    """
    db_profile = CompanyProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/", response_model=CompanyProfileRead)
def read_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve current company profile by user_id.
    """
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/", response_model=CompanyProfileRead)
def update_profile(user_id: str, profile_update: CompanyProfileUpdate, db: Session = Depends(get_db)):
    """
    Update company profile.
    """
    db_profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.post("/past-performance", response_model=PastPerformanceRead)
def create_past_performance(pp: PastPerformanceCreate, db: Session = Depends(get_db)):
    """
    Add a past performance record.
    """
    db_pp = PastPerformance(**pp.model_dump())
    db.add(db_pp)
    db.commit()
    db.refresh(db_pp)
    return db_pp

@router.get("/past-performance", response_model=List[PastPerformanceRead])
def read_past_performances(company_profile_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve all past performance records for a profile.
    """
    return db.query(PastPerformance).filter(PastPerformance.company_profile_id == company_profile_id).all()
