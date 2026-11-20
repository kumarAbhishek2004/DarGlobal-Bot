from pydantic import BaseModel, Field
from typing import List, Optional, Any

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question or real estate search query")
    top_k: Optional[int] = Field(default=4, ge=1, le=10, description="Number of top retrieved sources to return")
    history: Optional[List[Dict[str, Any]]] = Field(default=[], description="Previous conversation turns for context memory")
    session_id: Optional[str] = Field(default=None, description="Optional session identifier")

class SourceItem(BaseModel):
    title: Optional[Any] = None
    source: Optional[Any] = None
    brand: Optional[Any] = None
    location: Optional[Any] = None
    country: Optional[Any] = None
    property_type: Optional[Any] = None
    price: Optional[Any] = None
    bedrooms: Optional[Any] = None
    handover_date: Optional[Any] = None
    url: Optional[Any] = None
    relevance_score: Optional[float] = None

class ChatResponse(BaseModel):
    query: str
    answer: str
    model: str
    sources: List[SourceItem]
    latency_ms: float

class HealthResponse(BaseModel):
    status: str
    indexed_documents: int
    indexed_chunks: int
    active_model: str
    version: str = "1.0.0"

class ProjectItem(BaseModel):
    id: Optional[Any] = None
    source: Optional[Any] = None
    title: Optional[Any] = None
    brand: Optional[Any] = None
    city: Optional[Any] = None
    country: Optional[Any] = None
    price: Optional[Any] = None
    property_type: Optional[Any] = None
    url: Optional[Any] = None
