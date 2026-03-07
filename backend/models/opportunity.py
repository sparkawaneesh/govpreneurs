import uuid
from sqlalchemy import Column, String, Text, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .database import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core Identifiers
    notice_id = Column(String, index=True, nullable=False)
    solicitation_number = Column(String)
    
    # Basic Info
    title = Column(String)
    agency = Column(String)
    department = Column(String)
    
    # Categorization
    naics_code = Column(String, index=True)
    naics_description = Column(String)
    set_aside_type = Column(String)
    
    # Detailed Content
    description = Column(Text)
    scope_of_work = Column(Text)
    
    # Dates
    response_deadline = Column(DateTime, index=True)
    posted_date = Column(DateTime)
    modified_date = Column(DateTime)
    
    # Location & Value
    place_of_performance_city = Column(String)
    place_of_performance_state = Column(String)
    place_of_performance_country = Column(String)
    estimated_value = Column(String)
    contract_type = Column(String)
    
    # JSON Data
    attachments = Column(JSON) # List of attachment metadata
    keywords = Column(JSON) # List of extracted keywords
    
    # Sync Metadata
    last_synced_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Explicit indexes as requested (though redundant with index=True on Columns)
    __table_args__ = (
        Index('ix_opportunities_notice_id', 'notice_id'),
        Index('ix_opportunities_naics_code', 'naics_code'),
        Index('ix_opportunities_response_deadline', 'response_deadline'),
    )

    def __repr__(self):
        return f"<Opportunity(notice_id='{self.notice_id}', title='{self.title}')>"
