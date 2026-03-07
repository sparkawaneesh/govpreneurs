from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict
from fastapi.responses import StreamingResponse
from api.schemas.proposal import ProposalRequest, ProposalResponse, RefinementRequest, RefinementResponse
from services.proposal_generation_service import ProposalGenerationService
from services.export_service import ExportService
from auth.auth_router import get_current_user
from middleware.rate_limiter import limiter

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/proposals", 
    tags=["proposals"],
    dependencies=[Depends(get_current_user)]
)
generation_service = ProposalGenerationService()
export_service = ExportService()

@router.post("/generate", response_model=ProposalResponse)
@limiter.limit("5/minute")
async def generate_proposal(request: ProposalRequest):
    """
    Generate a proposal based on RFP and Company context.
    """
    return generation_service.generate_proposal(request)

@router.post("/export/docx")
async def export_proposal_docx(proposal: Dict = Body(...)):
    """
    Exports a proposal to a DOCX file.
    """
    logger.info("Received export request for DOCX.")
    
    try:
        buffer = export_service.generate_docx(proposal)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=proposal.docx"}
        )
        
    except Exception as e:
        logger.error(f"DOCX export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/export/pdf")
async def export_proposal_pdf(proposal: Dict = Body(...)):
    """
    Exports a proposal to a PDF file.
    """
    logger.info("Received export request for PDF.")
    
    try:
        buffer = export_service.generate_pdf(proposal)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=proposal.pdf"}
        )
        
    except Exception as e:
        logger.error(f"PDF export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/refine", response_model=RefinementResponse)
@limiter.limit("10/minute")
async def refine_proposal_section(request: RefinementRequest):
    """
    Refines a proposal section using the AI refinement logic.
    """
    logger.info(f"Received refinement request.")
    
    try:
        updated_text = generation_service.refine_section(
            section_text=request.section_text,
            instruction=request.instruction
        )
        
        return {
            "updated_text": updated_text
        }
        
    except Exception as e:
        logger.error(f"Proposal refinement API failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal_endpoint(request: ProposalRequest):
    """
    Triggers the RAG-based proposal generation process.
    """
    logger.info(f"Received proposal generation request for Opportunity: {request.opportunity_id}, Company: {request.company_id}")
    
    try:
        result = generation_service.generate_proposal(
            opportunity_id=str(request.opportunity_id),
            company_id=str(request.company_id)
        )
        
        return {
            "opportunity_id": request.opportunity_id,
            "sections": result.get("sections", [])
        }
        
    except Exception as e:
        logger.error(f"Proposal generation API failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
