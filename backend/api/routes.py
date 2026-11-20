import os
import json
import logging
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from .schemas import ChatRequest, ChatResponse, HealthResponse, ProjectItem
from backend.services.chat_service import ChatService
from backend.indexing.build import build_indices

logger = logging.getLogger(__name__)

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHUNKS_PATH = DATA_DIR / "chunks" / "chunks.json"
CORPUS_PATH = DATA_DIR / "processed" / "corpus.json"

_chat_service: ChatService = None

def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(data_dir=DATA_DIR)
    return _chat_service

@router.get("/health", response_model=HealthResponse)
@router.get("/api/health", response_model=HealthResponse)
def health_check():
    doc_count = 0
    chunk_count = 0

    if CORPUS_PATH.exists():
        try:
            with open(CORPUS_PATH, "r", encoding="utf-8") as f:
                doc_count = len(json.load(f))
        except Exception:
            pass

    if CHUNKS_PATH.exists():
        try:
            with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                chunk_count = len(json.load(f))
        except Exception:
            pass

    model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    return HealthResponse(
        status="healthy",
        indexed_documents=doc_count,
        indexed_chunks=chunk_count,
        active_model=model
    )

@router.post("/chat", response_model=ChatResponse)
@router.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    try:
        service = get_chat_service()
        result = service.answer_query(req.query, top_k=req.top_k)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/projects", response_model=List[ProjectItem])
def list_projects():
    """Returns catalog of all indexed luxury projects and properties."""
    if not CORPUS_PATH.exists():
        return []
    try:
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            docs = json.load(f)
        items = []
        for d in docs:
            loc = d.get("location") or {}
            items.append(ProjectItem(
                id=str(d.get("id")),
                source=d.get("source", "Real Estate"),
                title=d.get("title", ""),
                brand=d.get("developer_or_brand"),
                city=loc.get("city", ""),
                country=loc.get("country", ""),
                price=d.get("price", "TBA"),
                property_type=d.get("property_type", "Residential"),
                url=d.get("url", "")
            ))
        return items
    except Exception as e:
        logger.error(f"Failed to load projects: {e}")
        return []

@router.post("/api/rebuild-index")
def trigger_rebuild_index(background_tasks: BackgroundTasks):
    """Asynchronously triggers re-indexing of the dataset."""
    background_tasks.add_task(build_indices)
    return {"message": "Index rebuild triggered in background."}
