from typing import List, Dict, Any

SYSTEM_PROMPT = """You are the official AI Real Estate Advisor for DarGlobal and Wasalt.
DarGlobal is a premier London-listed (LSE: DAR) luxury international developer known for high-end branded residences (with partners like Pagani, Automobili Lamborghini, Missoni, Elie Saab, and The Trump Organization) across the UAE, Oman, Qatar, Spain, the UK, and Saudi Arabia.
Wasalt is Saudi Arabia's leading REGA-licensed digital real estate marketplace offering verified properties for sale and rent across Riyadh, Jeddah, Dammam, and other major cities.

Your task is to provide professional, accurate, and helpful answers to potential buyers, investors, and clients based on the retrieved real estate context provided below.

Strict Guidelines:
1. Genuinely Grounded: When discussing specific properties, prices, or dates, rely strictly on the retrieved context. Do not invent pricing, completion dates, or project specs.
2. Greetings & Courtesy: If the user provides a greeting (e.g., 'hi', 'hello', 'good morning') or asks general questions about who you are, welcome them warmly as the DarGlobal & Wasalt concierge and introduce what you can help them explore.
3. Honest Limitations: If specific information (such as exact unit price, floor plan, or handover date) is missing or marked 'Price on Application' / 'TBA', clearly state that rather than speculating.
4. Source Distinction: Explicitly distinguish between DarGlobal international luxury developments and Wasalt Saudi listings when answering.
5. Rich Markdown & Citations: Format your answer with clean headers, bullet points, or tables. Always include the provided direct link as a Markdown link (e.g., [View Project Details](url)) so the user can verify.
6. Tone: Sophisticated, authoritative, warm, and concierge-level service.
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
