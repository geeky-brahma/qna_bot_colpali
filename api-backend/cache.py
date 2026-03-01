from pinecone import Pinecone, ServerlessSpec
from config import settings
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

class PineconeCache:
    """
    Vector database cache using Pinecone for deduplicating similar queries.
    Stores query embeddings and results.
    """

    def __init__(self):
        self.client = None
        self.index = None
        self._initialize()

    def _initialize(self):
        """Initialize Pinecone connection."""
        try:
            if not settings.pinecone_api_key:
                logger.warning("Pinecone API key not set - cache disabled")
                return

            self.client = Pinecone(api_key=settings.pinecone_api_key)
            
            # List existing indexes
            indexes = self.client.list_indexes()
            index_names = [idx.name for idx in indexes.indexes] if indexes.indexes else []

            # Create index if doesn't exist
            if settings.pinecone_index_name not in index_names:
                logger.info(f"Creating Pinecone index: {settings.pinecone_index_name}")
                self.client.create_index(
                    name=settings.pinecone_index_name,
                    dimension=768,  # ColPali embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="gcp",
                        region="us-west1"
                    )
                )
                # Wait for index to be ready
                time.sleep(10)

            self.index = self.client.Index(settings.pinecone_index_name)
            logger.info("✓ Pinecone cache initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            self.client = None
            self.index = None

    def is_available(self) -> bool:
        """Check if Pinecone cache is available."""
        return self.index is not None

    async def get_similar_query(
        self,
        embedding: list[float],
        subject: str,
        threshold: float = 0.95
    ) -> Optional[dict]:
        """
        Search for similar cached query.
        
        Returns:
            Cached result if found, else None
        """
        if not self.is_available():
            return None

        try:
            # Search with metadata filter for subject
            results = self.index.query(
                vector=embedding,
                top_k=1,
                include_metadata=True,
                filter={
                    "subject": {"$eq": subject}
                }
            )

            if results.matches and len(results.matches) > 0:
                match = results.matches[0]
                if match.score >= threshold:
                    logger.info(f"Cache hit with score: {match.score}")
                    return match.metadata

            return None

        except Exception as e:
            logger.error(f"Error searching Pinecone cache: {str(e)}")
            return None

    async def store_result(
        self,
        query: str,
        embedding: list[float],
        subject: str,
        answer: str,
        sourcePages: list[int],
        userEmail: str
    ):
        """Store query result in cache."""
        if not self.is_available():
            return

        try:
            vector_id = f"{subject}_{hash(query) % 10000000}"

            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "query": query,
                        "subject": subject,
                        "answer": answer,
                        "sourcePages": sourcePages,
                        "userEmail": userEmail,
                        "timestamp": int(time.time())
                    }
                }]
            )

            logger.info(f"Stored result in cache: {vector_id}")

        except Exception as e:
            logger.error(f"Error storing in Pinecone cache: {str(e)}")

    async def health_check(self) -> bool:
        """Check Pinecone connection."""
        if not self.is_available():
            return False

        try:
            stats = self.index.describe_index_stats()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {str(e)}")
            return False


cache = PineconeCache()
