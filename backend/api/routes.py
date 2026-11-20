import os
import json
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from .schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ProjectItem,
    ThreadItem,
    CreateThreadRequest,
    ThreadDetailResponse,
)
from backend.services.chat_service import ChatService
from backend.indexing.build import build_indices
from backend.db.database import (
    init_db,
    create_thread,
    get_all_threads,
    get_thread_by_id,
    save_message_to_thread,
    update_thread_title_from_query,
    delete_thread_by_id,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize SQLite database schema
init_db()

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

@router.get("/api/threads", response_model=List[ThreadItem])
def list_threads():
    """Returns list of previous chat threads for ChatGPT-style history sidebar."""
    return get_all_threads()

@router.post("/api/threads", response_model=ThreadItem)
def create_new_thread(req: Optional[CreateThreadRequest] = None):
    """Creates a new conversation thread."""
    title = req.title if req else "New Conversation"
    return create_thread(title=title)

@router.get("/api/threads/{thread_id}", response_model=ThreadDetailResponse)
def get_thread_detail(thread_id: str):
    """Retrieves full conversation history for a given thread."""
    thread = get_thread_by_id(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread

@router.delete("/api/threads/{thread_id}")
def delete_thread(thread_id: str):
    """Deletes a conversation thread and all its stored messages."""
    success = delete_thread_by_id(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"status": "deleted", "thread_id": thread_id}

@router.post("/chat", response_model=ChatResponse)
@router.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    try:
        service = get_chat_service()

        # Resolve or create thread in SQLite
        thread_id = req.thread_id
        if not thread_id:
            thread = create_thread(title=req.query[:45])
            thread_id = thread["id"]
        else:
            existing = get_thread_by_id(thread_id)
            if not existing:
                create_thread(thread_id=thread_id, title=req.query[:45])

        # Resolve conversational history: use provided or load from DB
        history = req.history
        if not history:
            thread_data = get_thread_by_id(thread_id)
            if thread_data and thread_data.get("messages"):
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in thread_data["messages"]
                ]

        # 1. Save incoming user message to SQLite
        save_message_to_thread(thread_id, role="user", content=req.query)
        update_thread_title_from_query(thread_id, req.query)

        # 2. Generate answer with context
        result = service.answer_query(req.query, top_k=req.top_k, history=history)

        # 3. Save assistant response and sources to SQLite
        save_message_to_thread(
            thread_id=thread_id,
            role="assistant",
            content=result.get("answer", ""),
            sources=result.get("sources", []),
            model=result.get("model", "")
        )

        result["thread_id"] = thread_id
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
