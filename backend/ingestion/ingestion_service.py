import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.opportunity import Opportunity
from ingestion.sam_client import SAMGovClient

# Setup logging
logger = logging.getLogger(__name__)

class OpportunityIngestionService:
    """
    Service to handle the ingestion of opportunities from SAM.gov into the database.
    """

    def __init__(self, db_session: Session, sam_client: SAMGovClient = None):
        self.db = db_session
        self.sam_client = sam_client or SAMGovClient()

    def ingest_opportunities(self, posted_from: str = None, modified_since: str = None):
        """
        Fetches all opportunities from SAM.gov and upserts them into the database.
        """
        logger.info("Starting opportunity ingestion process...")
        
        try:
            # 1. Fetch all normalized opportunities from SAM.gov
            raw_opportunities = self.sam_client.fetch_all_opportunities(
                posted_from=posted_from, 
                modified_since=modified_since
            )
            
            total_fetched = len(raw_opportunities)
            inserted_count = 0
            updated_count = 0
            skipped_count = 0

            # 2. Iterate and upsert
            for opp_data in raw_opportunities:
                notice_id = opp_data.get("notice_id")
                if not notice_id:
                    logger.warning("Found opportunity without notice_id, skipping.")
                    continue

                # Check if opportunity exists
                existing_opp = self.db.query(Opportunity).filter(
                    Opportunity.notice_id == notice_id
                ).first()

                if existing_opp:
                    # Update if modified_date is newer
                    new_mod_date = opp_data.get("modified_date")
                    if new_mod_date and (not existing_opp.modified_date or new_mod_date > existing_opp.modified_date):
                        self._update_opportunity(existing_opp, opp_data)
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Insert new opportunity
                    new_opp = Opportunity(**opp_data)
                    new_opp.last_synced_at = datetime.utcnow()
                    self.db.add(new_opp)
                    inserted_count += 1

            # 3. Commit changes
            self.db.commit()
            
            logger.info(
                f"Ingestion complete: Total={total_fetched}, "
                f"Inserted={inserted_count}, Updated={updated_count}, "
                f"Skipped={skipped_count}"
            )
            
            return {
                "total_fetched": total_fetched,
                "inserted": inserted_count,
                "updated": updated_count,
                "skipped": skipped_count
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during ingestion: {str(e)}")
            raise

    def _update_opportunity(self, existing_opp: Opportunity, new_data: Dict[str, Any]):
        """
        Updates an existing opportunity record with new data.
        """
        for key, value in new_data.items():
            setattr(existing_opp, key, value)
        
        existing_opp.last_synced_at = datetime.utcnow()
        logger.debug(f"Updated opportunity: {existing_opp.notice_id}")
