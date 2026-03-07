import os
import uuid
import logging
import hashlib
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from cache.cache_service import CacheService

# Setup logging
logger = logging.getLogger(__name__)

class CompanyVectorService:
    """
    Service to convert company capabilities and past performance into vector embeddings.
    """

    def __init__(self, index_name: str = "company-profiles"):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.index_name = index_name

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

    def embed_capabilities(self, company_profile: Any):
        """
        Embeds the capabilities statement of a company.
        """
        capabilities_text = getattr(company_profile, "capabilities_statement", None)
        company_id = str(getattr(company_profile, "id"))

        if not capabilities_text:
            logger.warning(f"No capabilities statement for company {company_id}")
            return

        logger.info(f"Generating embedding for capabilities statement of company {company_id}")

        metadata = {
            "company_id": company_id,
            "type": "capability"
        }

        self._upsert_to_vectorstore([capabilities_text], [metadata], [str(uuid.uuid4())])

    def embed_past_performance(self, past_performance_records: List[Any]):
        """
        Embeds a list of past performance records.
        """
        if not past_performance_records:
            logger.warning("No past performance records provided for embedding.")
            return

        texts = []
        metadatas = []
        ids = []

        for record in past_performance_records:
            company_id = str(getattr(record, "company_profile_id"))
            project_name = getattr(record, "project_name")
            description = getattr(record, "description")

            if not description:
                continue

            # Construct meaningful text for embedding
            full_text = f"Project: {project_name}. Client: {getattr(record, 'client')}. Description: {description}"
            
            texts.append(full_text)
            metadatas.append({
                "company_id": company_id,
                "type": "past_performance",
                "project_name": project_name
            })
            ids.append(str(uuid.uuid4()))

        if texts:
            logger.info(f"Generating {len(texts)} embeddings for past performance records.")
            self._upsert_to_vectorstore(texts, metadatas, ids)

    def _upsert_to_vectorstore(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Helper for bulk upsert to Pinecone.
        """
        try:
            PineconeVectorStore.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                ids=ids,
                index_name=self.index_name
            )
            logger.info(f"Successfully upserted {len(texts)} vectors to {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to upsert vectors to Pinecone: {str(e)}")
            raise

    def similarity_search(self, query: str, company_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a similarity search in the company-profiles index.
        """
        # Cache Check
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cache_key = f"company_context:{company_id}:{query_hash}:{k}"
        cached_results = self.cache.get(cache_key)
        if cached_results:
            logger.info(f"Cache HIT for company context: {company_id}")
            return cached_results

        try:
            vectorstore = PineconeVectorStore(
                index=self.index,
                embedding=self.embeddings,
                text_key="text"
            )

            results = vectorstore.similarity_search_with_score(
                query,
                k=k,
                filter={"company_id": company_id}
            )

            res_list = [
                {
                    "text": res[0].page_content,
                    "metadata": res[0].metadata,
                    "score": float(res[1])
                }
                for res in results
            ]
            
            # Cache results
            self.cache.set(cache_key, res_list, ttl=900)
            
            return res_list
        except Exception as e:
            logger.error(f"Similarity search failed for company {company_id}: {str(e)}")
            raise
