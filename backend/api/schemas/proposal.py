from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional, Dict

class ProposalSection(BaseModel):
    title: str
    content: str
    citations: Optional[List[Dict[str, int]]] = None

class ProposalRequest(BaseModel):
    opportunity_id: UUID
    company_id: UUID

class ProposalResponse(BaseModel):
    opportunity_id: UUID
    sections: List[ProposalSection]

class RefinementRequest(BaseModel):
    section_text: str
    instruction: str

class RefinementResponse(BaseModel):
    updated_text: str
