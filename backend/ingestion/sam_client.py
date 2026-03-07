import requests
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SAMGovClient:
    """
    Client for interacting with the SAM.gov Opportunities API.
    """
    BASE_URL = "https://api.sam.gov/opportunities/v2/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SAM_API_KEY")
        if not self.api_key:
            logger.warning("SAM_API_KEY not found in environment or provided to client.")

    def search_opportunities(
        self, 
        posted_from: Optional[str] = None, 
        modified_since: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for opportunities with pagination.
        Dates should be in mm/dd/yyyy format as per SAM.gov API docs.
        """
        params = {
            "api_key": self.api_key,
            "limit": limit,
            "offset": offset
        }

        if posted_from:
            params["postedFrom"] = posted_from
        if modified_since:
            params["modifiedSince"] = modified_since

        logger.info(f"Calling SAM.gov API: offset={offset}, limit={limit}")
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            count = len(data.get("opportunitiesData", []))
            logger.info(f"Received {count} opportunities from SAM.gov")
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except requests.exceptions.Timeout:
            logger.error("The request timed out")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise
        except ValueError:
            logger.error("Response is not valid JSON")
            raise

    def fetch_all_opportunities(
        self, 
        posted_from: Optional[str] = None, 
        modified_since: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Iterate through all pages and aggregate opportunities.
        """
        all_opportunities = []
        limit = 100
        offset = 0
        
        while True:
            data = self.search_opportunities(
                posted_from=posted_from, 
                modified_since=modified_since, 
                limit=limit, 
                offset=offset
            )
            
            opportunities = data.get("opportunitiesData", [])
            if not opportunities:
                break
                
            all_opportunities.extend([self._normalize_opportunity(opp) for opp in opportunities])
            
            # Check if there are more results
            total_records = data.get("totalRecords", 0)
            offset += limit
            if offset >= total_records:
                break
                
        logger.info(f"Successfully fetched and normalized {len(all_opportunities)} total opportunities")
        return all_opportunities

    def _normalize_opportunity(self, raw_opp: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize internal SAM.gov fields to match our database schema.
        """
        # Note: SAM.gov API fields vary, this handles common mappings
        return {
            "notice_id": raw_opp.get("noticeId"),
            "solicitation_number": raw_opp.get("solicitationNumber"),
            "title": raw_opp.get("title"),
            "agency": raw_opp.get("fullParentPathName"), # Often contains Dept/Agency hierarchy
            "department": raw_opp.get("parentName"),
            "naics_code": raw_opp.get("naicsCode"),
            "naics_description": raw_opp.get("naicsDescription"),
            "set_aside_type": raw_opp.get("typeOfSetAsideDescription"),
            "description": raw_opp.get("description"),
            "response_deadline": self._parse_date(raw_opp.get("responseDeadLine")),
            "posted_date": self._parse_date(raw_opp.get("postedDate")),
            "modified_date": self._parse_date(raw_opp.get("modifiedDate")),
            "place_of_performance_city": raw_opp.get("placeOfPerformanceCity"),
            "place_of_performance_state": raw_opp.get("placeOfPerformanceState"),
            "place_of_performance_country": raw_opp.get("placeOfPerformanceCountry"),
            "estimated_value": raw_opp.get("baseAndAllOptionsValue"), # Example field for value
            "attachments": raw_opp.get("resourceLinks", []), # Often contains document URLs
            "keywords": raw_opp.get("keywords", []),
        }

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """ Helper to parse ISO format dates from API """
        if not date_str:
            return None
        try:
            # SAM.gov usually returns ISO strings or YYYY-MM-DD
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except (ValueError, TypeError):
                return None
