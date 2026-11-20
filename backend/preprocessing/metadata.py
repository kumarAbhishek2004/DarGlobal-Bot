from typing import Dict, Any

def enrich_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Adds structured filter tags to each chunk for hybrid routing."""
    price_num = chunk.get("price_numeric")
    price_tier = "Ultra-Luxury"
    if price_num:
        if price_num < 1000000:
            price_tier = "Affordable (< 1M)"
        elif price_num < 3000000:
            price_tier = "Mid-Luxury (1M - 3M)"
        elif price_num < 10000000:
            price_tier = "High-End Luxury (3M - 10M)"
        else:
            price_tier = "Trophy Asset (> 10M)"
    
    chunk["price_tier"] = price_tier
    chunk["is_darglobal"] = chunk.get("source") == "DarGlobal"
    chunk["is_wasalt"] = chunk.get("source") == "Wasalt"
    return chunk
