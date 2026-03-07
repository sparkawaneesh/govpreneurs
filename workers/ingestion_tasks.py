import logging
import sys
import os
from celery_app import app

# Add backend to sys.path to allow importing backend services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ingestion.ingestion_service import OpportunityIngestionService
from models.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task
def ingest_opportunities_task():
    """
    Celery task to trigger the opportunity ingestion process.
    """
    logger.info("Celery Task ingest_opportunities_task started.")
    
    db = SessionLocal()
    try:
        service = OpportunityIngestionService(db_session=db)
        # Passing no dates defaults to fetching latest/all as per service logic
        results = service.ingest_opportunities()
        
        logger.info(
            f"Celery Task ingest_opportunities_task completed. "
            f"Processed results: {results}"
        )
        return results
        
    except Exception as e:
        logger.error(f"Celery Task ingest_opportunities_task failed: {str(e)}")
        raise
    finally:
        db.close()
