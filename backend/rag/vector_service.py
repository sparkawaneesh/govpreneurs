import os
import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import sentry_sdk
from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from cache.cache_service import CacheService

# Setup logging
logger = logging.getLogger(__name__)

class VectorService:
    """
    Service to handle vector embeddings and storage in Pinecone.
    """

    def __init__(self, index_name: Optional[str] = None):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "govpreneurs-rfps")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key or not self.gemini_api_key:
            logger.warning("Pinecone or Gemini API keys missing from environment.")

        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        
        # Initialize Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.gemini_api_key
        )

        self.cache = CacheService()

        # Ensure index exists
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """
        Check if index exists, create if not.
        """
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,  # Dimension for models/embedding-001
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {str(e)}")
            raise

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Generates embeddings for chunks and upserts them to Pinecone.
        """
        if not chunks:
            logger.warning("No chunks provided for upsert.")
            return

        timestamp = datetime.utcnow().isoformat()
        logger.info(f"timestamp={timestamp}, service=VectorService, operation=upsert_chunks, status=started, count={len(chunks)}")
        
        try:
            texts = [c["text"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            ids = [c["chunk_id"] for c in chunks]

            # Use LangChain's Pinecone integration for bulk upsert
            PineconeVectorStore.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                ids=ids,
                index_name=self.index_name
            )
            
            logger.info(f"timestamp={timestamp}, service=VectorService, operation=upsert_chunks, status=success")
            
        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.error(f"timestamp={timestamp}, service=VectorService, operation=upsert_chunks, status=error, error={str(e)}")
            raise

    def similarity_search(self, query: str, opportunity_id: Optional[str] = None, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a similarity search in the vector database.
        Optionally filter by opportunity_id.
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Cache Check
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cache_key = f"rfp_chunks:{opportunity_id or 'all'}:{query_hash}:{k}"
        cached_results = self.cache.get(cache_key)
        if cached_results:
            logger.info(f"timestamp={timestamp}, service=VectorService, operation=similarity_search, status=cache_hit, opp_id={opportunity_id}")
            return cached_results

        logger.info(f"timestamp={timestamp}, service=VectorService, operation=similarity_search, status=started, opp_id={opportunity_id}")
        
        try:
            # Initialize vector store for search
            vectorstore = PineconeVectorStore(
                index=self.index,
                embedding=self.embeddings,
                text_key="text"
            )

            filter_dict = {}
            if opportunity_id:
                filter_dict["opportunity_id"] = opportunity_id

            # Use similarity_search_with_score to get the score
            results_with_scores = vectorstore.similarity_search_with_score(
                query, 
                k=k, 
                filter=filter_dict if filter_dict else None
            )

            res_list = [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                }
                for doc, score in results_with_scores
            ]
            
            # Cache results
            self.cache.set(cache_key, res_list, ttl=900)
            
            logger.info(f"timestamp={timestamp}, service=VectorService, operation=similarity_search, status=success, results={len(res_list)}")
            return res_list

        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.error(f"timestamp={timestamp}, service=VectorService, operation=similarity_search, status=error, error={str(e)}")
            raise
