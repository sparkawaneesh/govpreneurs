import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from ingestion.sam_client import SAMGovClient

def test_client_initialization():
    client = SAMGovClient(api_key="test_key")
    assert client.api_key == "test_key"
    print("[PASSED] Client initialization passed")

def test_normalization():
    client = SAMGovClient(api_key="test_key")
    raw_opp = {
        "noticeId": "123",
        "title": "Test Title",
        "postedDate": "2023-10-01T00:00:00Z"
    }
    normalized = client._normalize_opportunity(raw_opp)
    assert normalized["notice_id"] == "123"
    assert normalized["title"] == "Test Title"
    assert normalized["posted_date"] is not None
    print("[PASSED] Normalization passed")

if __name__ == "__main__":
    test_client_initialization()
    test_normalization()
    print("All verification tests passed!")
