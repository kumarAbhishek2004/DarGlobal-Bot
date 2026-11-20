import re
from typing import Optional

def clean_text(text: Optional[str]) -> str:
    """Cleans raw text by stripping HTML tags, extra whitespace, and control characters."""
    if not text:
        return ""
    # Strip HTML tags if any remain
    text = re.sub(r"<[^>]+>", " ", text)
    # Replace non-breaking spaces
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    # Normalize multiple whitespace and newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()

def format_currency(amount: Optional[float], currency: str = "SAR") -> str:
    """Formats numeric amounts into readable currency strings."""
    if amount is None:
        return "Price on Application"
    try:
        val = float(amount)
        if val <= 0:
            return "Price on Application"
        return f"{val:,.0f} {currency}"
    except (ValueError, TypeError):
        return str(amount)

def clean_human_response(text: Optional[str]) -> str:
    """Parses raw LLM generation into natural, human-written concierge text:
    - Strips internal thinking/reasoning blocks ('Here's a thinking process:', <think> tags, analysis outlines).
    - Removes AI asterisks (* and **) and replaces them with clean text and bullet points (•).
    - Removes robotic AI meta-talk ('As an AI', 'Based on Document 1').
    """
    if not text:
        return ""

    # 1. Strip <think>...</think> or [think]...[/think] tags
    text = re.sub(r"(?is)<\s*think\s*>.*?<\s*/\s*think\s*>", "", text)
    text = re.sub(r"(?is)\[\s*think\s*\].*?\[\s*/\s*think\s*\]", "", text)

    # 2. Strip "Here's a thinking process:" / "Thinking Process:" commentary and step-by-step planning
    thinking_match = re.search(r"(?is)^.*?(?:here(?:'s|\s+is)\s+(?:a\s+)?thinking\s+process|thinking\s+process|chain\s+of\s+thought):?", text)
    if thinking_match:
        blocks = text.split("\n\n")
        filtered_blocks = []
        is_analyzing = True
        for b in blocks:
            lower_b = b.lower()
            if any(marker in lower_b for marker in ["thinking process", "analyze user input", "identify relevant context", "check guidelines", "structure the response"]):
                continue
            if is_analyzing and (re.match(r"^\s*\d+[\.\)]\s+", b) or b.startswith("   - ") or b.startswith("- ")):
                continue
            is_analyzing = False
            filtered_blocks.append(b)

        if filtered_blocks:
            text = "\n\n".join(filtered_blocks).strip()

    # 3. Strip robotic AI preamble
    text = re.sub(r"(?i)^(?:as an ai|as a large language model|based on (?:the )?(?:retrieved |provided )?(?:context|documents?|doc \d+)[,\s:]*)\s*", "", text)
    text = re.sub(r"(?i)\b(according to the provided context|as an ai assistant|based on the context)\b[:,]?", "", text)

    # 4. Strip asterisks (*) and AI formatting symbols
    # Bold **text** -> text
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    # Italic *text* -> text
    text = re.sub(r"\*([^\*\n]+)\*", r"\1", text)
    # Convert list asterisks (* or -) to clean elegant bullet points (•)
    text = re.sub(r"(?m)^\s*[\*\-]\s+", "• ", text)
    # Remove any remaining stray asterisks
    text = text.replace("*", "")

    # 5. Clean markdown headers (### Header -> Header)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)

    # 6. Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text
