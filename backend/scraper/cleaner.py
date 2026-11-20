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
