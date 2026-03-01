"""
API router for query handling with caching.
"""

from fastapi import APIRouter, HTTPException
from models import QueryRequest, QueryResponse
from inference import inference_backend
from cache import cache
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Main query endpoint with caching.
    
    Flow:
    1. Try to find similar cached query
    2. If cache hit, return cached answer
    3. If cache miss, call inference backend
    4. Cache the result
    """
    start_time = time.time()
    
    try:
        # TODO: When inference backend is ready, get embedding here
        # For now, use a dummy embedding
        embedding = [0.0] * 768
        
        # Try cache
        logger.info(f"Query: {request.query} | Subject: {request.subject}")
        cached_result = await cache.get_similar_query(
            embedding=embedding,
            subject=request.subject
        )
        
        if cached_result:
            response_time = time.time() - start_time
            logger.info(f"Cache hit! Response time: {response_time:.2f}s")
            return QueryResponse(
                answer=cached_result["answer"],
                sourcePages=cached_result["sourcePages"],
                cached=True,
                responseTime=response_time
            )
        
        # Cache miss - call inference backend
        logger.info("Cache miss - calling inference backend")
        result = await inference_backend.query(
            text=request.query,
            subject=request.subject
        )
        
        # Store in cache
        await cache.store_result(
            query=request.query,
            embedding=embedding,
            subject=request.subject,
            answer=result["answer"],
            sourcePages=result["sourcePages"],
            userEmail=request.userEmail
        )
        
        response_time = time.time() - start_time
        logger.info(f"Inference completed. Response time: {response_time:.2f}s")
        
        return QueryResponse(
            answer=result["answer"],
            sourcePages=result["sourcePages"],
            cached=False,
            responseTime=response_time
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
