import os
import sys
import logging
from pathlib import Path

# Ensure project root is in sys.path regardless of execution working directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DarGlobal AI Real Estate Advisor",
    description="Clean, production-grade Hybrid-RAG Chatbot for DarGlobal & Wasalt real estate.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.on_event("startup")
def prewarm_indices_in_background():
    """Warms up the HybridRetriever and vector index in a background thread so server starts instantly."""
    import threading
    def _warmup():
        try:
            logger.info("Background thread: Warming up HybridRetriever and embedding indices...")
            from backend.api.routes import get_chat_service
            service = get_chat_service()
            _ = service.retriever
            logger.info("Background thread: HybridRetriever and FAISS are warm and ready!")
        except Exception as e:
            logger.warning(f"Background warmup encountered non-critical error: {e}")

    threading.Thread(target=_warmup, daemon=True).start()

# Mount frontend build static directory if available
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST_DIR.exists():
    logger.info(f"Serving static frontend from {FRONTEND_DIST_DIR}")
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("health") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Serve index.html with no-cache headers so browsers immediately see updates
        return FileResponse(
            FRONTEND_DIST_DIR / "index.html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
else:
    @app.get("/")
    def root_status():
        return {
            "service": "DarGlobal AI Real Estate API",
            "status": "online",
            "docs_url": "/docs",
            "health_url": "/api/health",
            "chat_url": "/api/chat"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
