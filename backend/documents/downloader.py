import os
import logging
import requests
import time
from typing import List, Dict, Any
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

class AttachmentDownloader:
    """
    Service to download solicitation PDF attachments for opportunities.
    """

    def __init__(self, base_storage_path: str = "storage/opportunities"):
        self.base_storage_path = Path(base_storage_path)
        self.base_storage_path.mkdir(parents=True, exist_ok=True)

    def download_attachments(self, opportunity: Any) -> List[str]:
        """
        Downloads PDF attachments for a given opportunity.
        Returns a list of local file paths.
        """
        opp_id = str(opportunity.id)
        attachments = opportunity.attachments or []
        
        opp_storage_dir = self.base_storage_path / opp_id
        opp_storage_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded_paths = []

        for attr in attachments:
            file_name = attr.get("file_name")
            file_type = attr.get("file_type", "").lower()
            url = attr.get("url")

            if not url or file_type != "pdf":
                continue

            if not file_name:
                file_name = url.split("/")[-1] or f"attachment_{int(time.time())}.pdf"
            
            if not file_name.lower().endswith(".pdf"):
                file_name += ".pdf"

            local_path = opp_storage_dir / file_name
            
            if self._download_file(url, local_path):
                downloaded_paths.append(str(local_path))

        return downloaded_paths

    def _download_file(self, url: str, destination: Path, max_retries: int = 3) -> bool:
        """
        Helper to download a file with retry logic and validation.
        """
        attempt = 0
        while attempt < max_retries:
            try:
                logger.info(f"Downloading {url} (Attempt {attempt+1}/{max_retries})")
                response = requests.get(url, timeout=60, stream=True)
                response.raise_for_status()

                with open(destination, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Validate file is not empty
                if destination.stat().st_size == 0:
                    logger.warning(f"Downloaded file {destination} is empty. Deleting.")
                    destination.unlink()
                    attempt += 1
                    continue

                logger.info(f"Successfully downloaded to {destination}")
                return True

            except (requests.exceptions.RequestException, IOError) as e:
                attempt += 1
                logger.error(f"Failed to download {url}: {str(e)}. Retrying...")
                if attempt < max_retries:
                    time.sleep(2 ** attempt) # Exponential backoff
                else:
                    logger.error(f"Max retries reached for {url}")
        
        return False
