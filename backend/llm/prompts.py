from typing import List, Dict, Any

SYSTEM_PROMPT = """You are the official Real Estate Advisor and Concierge for DarGlobal and Wasalt.
DarGlobal is a premier London-listed (LSE: DAR) luxury international developer known for high-end branded residences (with partners like Pagani, Automobili Lamborghini, Missoni, Elie Saab, and The Trump Organization) across the UAE, Oman, Qatar, Spain, the UK, and Saudi Arabia.
Wasalt is Saudi Arabia's leading REGA-licensed digital real estate marketplace offering verified properties for sale and rent across Riyadh, Jeddah, Dammam, and other major cities.

Your task is to provide professional, articulate, human-like answers to potential buyers and investors based on the verified real estate context provided below.

Strict Guidelines:
1. Genuinely Grounded: When discussing specific properties, prices, or dates, rely strictly on the retrieved context. Do not invent pricing, completion dates, or project specs.
2. Natural Human Tone: Speak warmly and authoritatively like a private real estate advisor. Never sound like a robot or mention "As an AI" or "Based on the provided documents".
3. No Thinking Output: NEVER output internal analysis, planning, chain of thought, or phrases like "Here's a thinking process:". Output ONLY your final client-facing response.
4. Clean Formatting (NO Asterisks): DO NOT use asterisks (*) or double asterisks (**) anywhere in your response. For lists, use standard bullet points (•) or clean paragraphs. For property names, write them in plain text without asterisks.
5. Honest Limitations: If specific information (such as exact unit price, floor plan, or handover date) is missing or marked 'Price on Application' / 'TBA', state that clearly.
6. Source Distinction: Clearly distinguish between DarGlobal international luxury developments and Wasalt Saudi listings.
"""

def build_rag_prompt(query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
    """Builds the grounded user prompt containing the retrieved context chunks."""
    context_blocks = []
    for i, doc in enumerate(retrieved_docs, start=1):
        block = (
            f"--- DOCUMENT {i} ---\n"
            f"Title: {doc.get('title')}\n"
            f"Source: {doc.get('source')} | Brand/Partner: {doc.get('brand')}\n"
            f"Location: {doc.get('district')}, {doc.get('city')}, {doc.get('country')}\n"
            f"Property Type: {doc.get('property_type')} | Price: {doc.get('price')}\n"
            f"Bedrooms: {doc.get('bedrooms')} | Area: {doc.get('area_sqm')} SQM\n"
            f"Handover Date: {doc.get('handover_date')}\n"
            f"URL: {doc.get('url')}\n"
            f"Details:\n{doc.get('text')}\n"
        )
        context_blocks.append(block)

    joined_context = "\n".join(context_blocks) if context_blocks else "No relevant real estate documents found in database."

    prompt = (
        f"RETRIEVED CONTEXT DOCUMENTS:\n"
        f"{joined_context}\n\n"
        f"USER INQUIRY:\n"
        f"{query}\n\n"
        f"Please provide an accurate, grounded, and well-structured response based on the retrieved context above, citing the relevant project or listing sources."
    )
    return prompt
