import os
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import sentry_sdk
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import Session

from models.database import SessionLocal
from models.opportunity import Opportunity
from services.proposal_retrieval_service import ProposalRetrievalService

# Setup logging
logger = logging.getLogger(__name__)

class ProposalGenerationService:
    """
    Service to generate structured government proposal drafts using RAG and GPT-4o.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY missing from environment.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=self.api_key,
            temperature=0.2
        )
        self.retrieval_service = ProposalRetrievalService()

    def refine_section(self, section_text: str, instruction: str) -> str:
        """
        Rewrite a proposal section according to a user instruction.
        """
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"timestamp={timestamp}, service=ProposalGenerationService, operation=refine_section, status=started")

        try:
            system_prompt = (
                "You are an expert Government Proposal Writer. "
                "Your goal is to refine and rewrite a specific proposal section based on user instructions.\n"
                "FOLLOW THESE STRICT RULES:\n"
                "1. Maintain a formal, professional government contracting tone.\n"
                "2. Follow the user's instruction precisely.\n"
                "3. DO NOT FABRICATE company capabilities or experience.\n"
                "4. Preserve the factual accuracy of the original text.\n"
                "5. Return ONLY the updated text of the section."
            )

            user_prompt = f"""
            ORIGINAL SECTION TEXT:
            {section_text}
            
            USER INSTRUCTION:
            {instruction}
            
            Refined Section Content:
            """

            response = self.llm.invoke([
                ("system", system_prompt),
                ("user", user_prompt)
            ])

            updated_text = response.content.strip()
            logger.info(f"timestamp={timestamp}, service=ProposalGenerationService, operation=refine_section, status=success")

            return updated_text

        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.error(f"timestamp={timestamp}, service=ProposalGenerationService, operation=refine_section, status=error, error={str(e)}")
            raise

    def generate_proposal(self, opportunity_id: str, company_id: str) -> Dict[str, Any]:
        """
        Orchestrates retrieval and generation to produce a proposal draft.
        """
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"timestamp={timestamp}, service=ProposalGenerationService, operation=generate_proposal, status=started, opp_id={opportunity_id}, comp_id={company_id}")

        try:
            # 1. Fetch Opportunity Metadata for context
            db = SessionLocal()
            opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
            opp_metadata = {
                "title": opportunity.title if opportunity else "N/A",
                "agency": opportunity.agency if opportunity else "N/A",
                "solicitation_number": opportunity.solicitation_number if opportunity else "N/A",
                "description": opportunity.description if opportunity else "N/A"
            }
            db.close()

            # 2. Retrieve Context (RFP Chunks and Company Experience)
            context = self.retrieval_service.retrieve_context(opportunity_id, company_id)
            
            rfp_text = "\n\n".join([
                f"[RFP Page {c.get('metadata', {}).get('page_start', 'Unknown')}] {c['text']}" 
                for c in context.get("rfp_context", [])
            ])
            experience_text = "\n\n".join([
                f"[{m['type'].upper()}] {m['project_name']}: {m['text']}" 
                for m in context.get("company_context", [])
            ])

            # 3. Build the Prompt
            system_prompt = (
                "You are an expert Government Proposal Writer. "
                "Your goal is to generate a highly professional, compliant, and persuasive proposal draft. "
                "FOLLOW THESE STRICT RULES:\n"
                "1. Use a formal, professional government contracting tone.\n"
                "2. ONLY use information provided in the context below.\n"
                "3. DO NOT FABRICATE experience or capabilities. If information is missing, state 'TBD' or note the missing data.\n"
                "4. Structure the response as a JSON object with a 'sections' array.\n"
                "5. For each section, include a 'citations' list containing the 'page' numbers from the RFP context that uniquely support that section."
            )

            user_prompt = f"""
            Generate a proposal for the following opportunity:
            
            OPPORTUNITY METADATA:
            Title: {opp_metadata['title']}
            Agency: {opp_metadata['agency']}
            Solicitation #: {opp_metadata['solicitation_number']}
            
            RFP REQUIREMENTS (Context with Page Numbers):
            {rfp_text}
            
            COMPANY CAPABILITIES AND PAST PERFORMANCE (Context):
            {experience_text}
            
            The proposal must include the following sections:
            - Executive Summary
            - Technical Approach
            - Relevant Experience
            - Capability Overview
            - Compliance Statement
            - Conclusion
            
            RESPONSE FORMAT:
            {{
                "sections": [
                    {{ 
                        "title": "Executive Summary", 
                        "content": "...",
                        "citations": [ {{ "page": 1 }}, {{ "page": 5 }} ]
                    }},
                    ...
                ]
            }}
            """

            # 4. Call LLM
            logger.info(f"timestamp={timestamp}, service=ProposalGenerationService, operation=generate_proposal, status=calling_llm")
            
            # Use json_object response format if the underlying chain supports it, 
            # or just rely on the prompt which is already very specific about JSON.
            # For Gemini with LangChain, we can use bind_tools or with_structured_output too.
            # But for a direct replacement that keeps the prompt as is:
            llm_with_json = self.llm.bind(response_mime_type="application/json")
            
            response = llm_with_json.invoke([
                ("system", system_prompt),
                ("user", user_prompt)
            ])

            # 5. Parse Result
            proposal_json = json.loads(response.content)
            
            sections = proposal_json.get("sections", [])
            logger.info(f"timestamp={timestamp}, service=ProposalGenerationService, operation=generate_proposal, status=success, sections={len(sections)}")

            return proposal_json

        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.error(f"timestamp={timestamp}, service=ProposalGenerationService, operation=generate_proposal, status=error, error={str(e)}")
            raise
