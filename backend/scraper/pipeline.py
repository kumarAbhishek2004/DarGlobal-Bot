import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from .wasalt import scrape_wasalt_listings
from .darglobal import scrape_darglobal_portfolio

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

def run_ingestion_pipeline() -> List[Dict[str, Any]]:
    """Runs the full ingestion pipeline for both DarGlobal and Wasalt."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Starting Data Ingestion Pipeline...")

    # 1. Scrape DarGlobal
    dg_docs = scrape_darglobal_portfolio()
    dg_raw_path = DATA_RAW_DIR / "darglobal.json"
    with open(dg_raw_path, "w", encoding="utf-8") as f:
        json.dump(dg_docs, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(dg_docs)} DarGlobal projects to {dg_raw_path}")

    # 2. Scrape Wasalt
    ws_docs = scrape_wasalt_listings()
    ws_raw_path = DATA_RAW_DIR / "wasalt.json"
    with open(ws_raw_path, "w", encoding="utf-8") as f:
        json.dump(ws_docs, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(ws_docs)} Wasalt listings to {ws_raw_path}")

    # Combine into unified knowledge corpus
    combined = dg_docs + ws_docs
    combined_path = DATA_PROCESSED_DIR / "corpus.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved combined corpus ({len(combined)} documents) to {combined_path}")

    return combined

if __name__ == "__main__":
    run_ingestion_pipeline()
