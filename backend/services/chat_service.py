import time
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from backend.retrieval.hybrid import HybridRetriever
from backend.llm.openrouter import OpenRouterClient
from backend.llm.prompts import SYSTEM_PROMPT, build_rag_prompt
from backend.scraper.cleaner import clean_human_response

logger = logging.getLogger(__name__)

class ChatService:
    """End-to-end conversational service for real estate inquiries."""

    def __init__(self, data_dir: Path, openrouter_key: Optional[str] = None):
        self.data_dir = Path(data_dir)
        self._retriever = None
        self.llm_client = OpenRouterClient(api_key=openrouter_key)

    @property
    def retriever(self) -> HybridRetriever:
        """Lazy-loads the hybrid retriever and embeddings model on demand."""
        if self._retriever is None:
            logger.info("Initializing HybridRetriever and vector indices...")
            self._retriever = HybridRetriever(self.data_dir)
            logger.info("HybridRetriever initialized successfully.")
        return self._retriever

    def _is_greeting(self, query: str) -> bool:
        """Detects conversational pleasantries and greetings to provide instant concierge response."""
        clean = re.sub(r"[^\w\s]", "", query).strip().lower()
        if not clean:
            return True

        pure_greetings = {
            "hi", "hii", "hiii", "hello", "helloo", "hey", "heyy", "greetings",
            "good morning", "good afternoon", "good evening", "howdy", "sup", "yo",
            "who are you", "what are you", "what can you do", "help", "start", "menu",
            "test", "ping"
        }
        if clean in pure_greetings:
            return True

        greeting_starters = ("hi ", "hii ", "hello ", "hey ", "greetings ", "good morning", "good afternoon", "good evening")
        if any(clean.startswith(prefix) for prefix in greeting_starters) and len(clean.split()) <= 4:
            return True

        conversational_short = {
            "hi there", "hello there", "hey there", "how are you", "how are you doing",
            "can you help me", "who created you", "who made you"
        }
        if clean in conversational_short:
            return True

        return False

    def answer_query(self, user_query: str, top_k: int = 4, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Processes user question through Hybrid Retrieval, Reranking, and LLM Generation with multi-turn context memory."""
        start_time = time.time()
        logger.info(f"Processing query: '{user_query}' (history turns: {len(history) if history else 0})")

        # Instant 0ms response for greetings (only on initial turn)
        if self._is_greeting(user_query) and not history:
            latency = round((time.time() - start_time) * 1000, 2)
            return {
                "query": user_query,
                "answer": (
                    "Hello! Welcome to the DarGlobal & Wasalt Real Estate Concierge.\n\n"
                    "I am your dedicated advisor for exploring our verified real estate portfolio:\n\n"
                    "• DarGlobal International Luxury: Ultra-prime branded residences across Dubai, Spain, Oman, Qatar, and London in partnership with prestigious marques including Pagani, Automobili Lamborghini, Elie Saab, and The Trump Organization.\n\n"
                    "• Wasalt Saudi Marketplace: Verified villas, apartments, and land for sale and rent across Riyadh, Jeddah, Dammam, and major Saudi hubs.\n\n"
                    "How may I assist you today? You can ask about:\n"
                    "• Tierra Viva luxury Lamborghini villas in Spain\n"
                    "• Pagani DaVinci Tower in Dubai\n"
                    "• Verified residential villas in Riyadh on Wasalt"
                ),
                "model": "concierge/instant",
                "sources": [],
                "latency_ms": latency
            }

        # Context-aware query expansion for follow-up questions (e.g. "what is its price?", "where is it located?")
        search_query = user_query
        if history:
            prev_user_queries = [
                str(h.get("content", "")) for h in history 
                if h.get("role") == "user" and h.get("content")
            ]
            if prev_user_queries:
                last_user_query = prev_user_queries[-1]
                pronouns = {"it", "its", "this", "that", "these", "those", "they", "them", "there", "here", "the project", "the villa"}
                words = set(re.findall(r"\b\w+\b", user_query.lower()))
                # If current query contains pronouns or is a brief follow-up (<= 6 words), enrich with last subject
                if (words & pronouns) or len(user_query.split()) <= 6:
                    search_query = f"{user_query} {last_user_query}"
                    logger.info(f"Enriched search query with context: '{search_query}'")

        # 1. Retrieve & Rerank Context Documents
        retrieved_docs = self.retriever.retrieve(search_query, top_k=top_k)

        # 2. Build Grounded User Prompt
        user_prompt = build_rag_prompt(user_query, retrieved_docs)

        # 3. Construct Multi-Turn Message History for LLM
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Inject up to last 4 conversation turns for context continuity
        if history:
            for turn in history[-4:]:
                role = str(turn.get("role", "user")).lower()
                content = str(turn.get("content", "")).strip()
                if role in ("user", "assistant") and content:
                    messages.append({
                        "role": role,
                        "content": content[:600] # keep recent turns concise for token budget
                    })

        # Append current grounded user query
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        # 3. Generate Answer with OpenRouter (with automatic model fallback)
        llm_res = self.llm_client.generate(messages)
        latency = round((time.time() - start_time) * 1000, 2)
        raw_answer = str(llm_res.get("content") or "").strip()
        # Parse and humanize output: strip AI thinking steps, asterisks, and robotic artifacts
        answer_text = clean_human_response(raw_answer)
        if not answer_text:
            answer_text = "I have reviewed the property context for your query. For full unit availability and private viewings, please contact DarGlobal or Wasalt directly."

        # 4. Format Sources for Frontend
        sources = []
        for doc in retrieved_docs:
            sources.append({
                "title": str(doc.get("title") or ""),
                "source": str(doc.get("source") or "Real Estate"),
                "brand": str(doc.get("brand")) if doc.get("brand") else None,
                "location": f"{doc.get('district', '')}, {doc.get('city', '')}".strip(", "),
                "country": str(doc.get("country") or ""),
                "property_type": str(doc.get("property_type") or "Residential"),
                "price": str(doc.get("price")) if doc.get("price") is not None else "Contact for pricing",
                "bedrooms": doc.get("bedrooms"),
                "handover_date": str(doc.get("handover_date")) if doc.get("handover_date") is not None else None,
                "url": str(doc.get("url") or "#"),
                "relevance_score": doc.get("relevance_score")
            })

        return {
            "query": user_query,
            "answer": answer_text,
            "model": llm_res.get("model", "openrouter/free"),
            "sources": sources,
            "latency_ms": latency
        }
