import uuid
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True, nullable=False) # Simplified user reference
    company_name = Column(String, nullable=False)
    
    # Core Data
    capabilities_statement = Column(Text)
    core_services = Column(JSON) # List of services
    naics_codes = Column(JSON) # List of NAICS codes
    certifications = Column(JSON) # List of certifications (SDVOSB, WOSB, etc.)
    
    # Metadata
    team_size = Column(String)
    location = Column(String)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    past_performances = relationship("PastPerformance", back_populates="company_profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CompanyProfile(name='{self.company_name}')>"
