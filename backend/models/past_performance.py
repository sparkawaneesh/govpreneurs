import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class PastPerformance(Base):
    __tablename__ = "past_performances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_profile_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id"), nullable=False)
    
    # Project Details
    project_name = Column(String, nullable=False)
    client = Column(String, nullable=False)
    description = Column(Text)
    contract_value = Column(Float) # Float for value comparison
    
    # Dates
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # Relationship
    company_profile = relationship("CompanyProfile", back_populates="past_performances")

    def __repr__(self):
        return f"<PastPerformance(project='{self.project_name}', client='{self.client}')>"
