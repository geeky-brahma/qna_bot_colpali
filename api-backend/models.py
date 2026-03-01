from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    subject: str = Field(...)
    userEmail: str = Field(...)

class QueryResponse(BaseModel):
    answer: str
    sourcePages: list[int]
    cached: bool
    responseTime: float

class CacheEntry(BaseModel):
    query: str
    subject: str
    answer: str
    sourcePages: list[int]
    embedding: list[float]
    userEmail: str
    timestamp: datetime
    ttl: int = 86400

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    pinecone_connected: bool
