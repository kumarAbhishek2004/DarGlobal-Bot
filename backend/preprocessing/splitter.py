from typing import List, Dict, Any

def create_document_chunk(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Transforms a raw normalized real estate record into an enriched, context-grounded searchable text chunk."""
    title = doc.get("title", "")
    source = doc.get("source", "Real Estate")
    brand = doc.get("developer_or_brand", "DarGlobal / Wasalt")
    loc = doc.get("location") or {}
    city = loc.get("city", "")
    district = loc.get("district", "")
    country = loc.get("country", "")
    prop_type = doc.get("property_type", "Residential")
    price = doc.get("price", "Price on Application")
    bedrooms = doc.get("bedrooms", "N/A")
    area = doc.get("area_sqm", "N/A")
    handover = doc.get("handover_date", "TBA")
    amenities = doc.get("amenities") or []
    amenities_str = ", ".join(amenities) if amenities else "Standard luxury amenities"
    description = doc.get("description", "")
    url = doc.get("url", "")

    # Construct dense semantic representation
    header = (
        f"[PROPERTY] {title}\n"
        f"[SOURCE] {source} | [BRAND/DEVELOPER] {brand}\n"
        f"[LOCATION] {district}, {city}, {country}\n"
        f"[TYPE] {prop_type} | [PRICE] {price}\n"
        f"[BEDROOMS] {bedrooms} | [AREA] {area} SQM | [HANDOVER] {handover}\n"
        f"[AMENITIES] {amenities_str}\n"
        f"[URL] {url}"
    )

    full_chunk_text = f"{header}\n\n[OVERVIEW & DETAILS]\n{description}".strip()

    return {
        "chunk_id": f"{doc.get('id', 'doc')}_c1",
        "doc_id": doc.get("id"),
        "source": source,
        "title": title,
        "brand": brand,
        "city": city,
        "district": district,
        "country": country,
        "property_type": prop_type,
        "price": price,
        "price_numeric": doc.get("price_numeric"),
        "currency": doc.get("currency", "SAR"),
        "bedrooms": bedrooms,
        "area_sqm": area,
        "handover_date": handover,
        "amenities": amenities,
        "url": url,
        "text": full_chunk_text
    }

def chunk_corpus(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunks an entire corpus of documents into enriched searchable chunks."""
    chunks = []
    for doc in docs:
        chunks.append(create_document_chunk(doc))
    return chunks
