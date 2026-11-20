from typing import Dict, Any, List
from .cleaner import clean_text, format_currency

def normalize_wasalt_property(raw_prop: Dict[str, Any]) -> Dict[str, Any]:
    """Converts a raw Wasalt property record from __NEXT_DATA__ into a clean structured document."""
    info = raw_prop.get("propertyInfo") or {}
    loc = raw_prop.get("location") or {}
    attrs = raw_prop.get("attributes") or []

    # Extract bedrooms, area, age from attributes list
    bedrooms = None
    built_up_area = None
    age = None
    for attr in attrs:
        k = attr.get("key")
        val = attr.get("value")
        if k == "noOfBedrooms":
            bedrooms = val
        elif k == "builtUpArea":
            built_up_area = val
        elif k == "completionYear":
            age = val

    title = info.get("title") or info.get("propertyName") or "Saudi Real Estate Property"
    city = info.get("city") or "Riyadh"
    district = info.get("district") or info.get("zone") or "Central"
    prop_type = info.get("propertySubType") or info.get("propertyMainType") or "Residential"
    sale_price = info.get("salePrice") or info.get("conversionPrice")
    curr = info.get("currencyType") or "SAR"
    slug = raw_prop.get("slug") or info.get("slug") or str(raw_prop.get("id", ""))
    url = f"https://wasalt.sa/en/property/{slug}" if slug else "https://wasalt.sa/en"

    # Amenities
    amenities = []
    for am in raw_prop.get("featureAmenities") or []:
        if isinstance(am, dict) and am.get("name"):
            amenities.append(am["name"])
        elif isinstance(am, str):
            amenities.append(am)

    desc_parts = [
        f"**{clean_text(title)}** is a {prop_type.lower()} available for {info.get('propertyFor', 'sale')} in {district}, {city}, Saudi Arabia.",
        f"Listed on Wasalt marketplace.",
        f"Price: {format_currency(sale_price, curr)}.",
    ]
    if bedrooms:
        desc_parts.append(f"Bedrooms: {bedrooms}.")
    if built_up_area:
        desc_parts.append(f"Built-Up Area: {built_up_area} SQM.")
    if age:
        desc_parts.append(f"Property Condition / Age: {age}.")
    if amenities:
        desc_parts.append(f"Features & Amenities: {', '.join(amenities)}.")

    full_description = clean_text(" ".join(desc_parts))

    return {
        "id": f"wasalt_{raw_prop.get('id', slug)}",
        "source": "Wasalt",
        "title": clean_text(title),
        "developer_or_brand": "Wasalt Marketplace Partner",
        "location": {
            "city": city,
            "district": district,
            "country": "Saudi Arabia",
            "lat": loc.get("lat"),
            "lon": loc.get("lon"),
            "address": info.get("address") or f"{district}, {city}"
        },
        "property_type": prop_type,
        "price": format_currency(sale_price, curr),
        "price_numeric": float(sale_price) if sale_price else None,
        "currency": curr,
        "bedrooms": bedrooms,
        "area_sqm": built_up_area,
        "amenities": amenities,
        "handover_date": age or "Ready / Handover Available",
        "description": full_description,
        "url": url
    }

def normalize_darglobal_project(raw_proj: Dict[str, Any]) -> Dict[str, Any]:
    """Converts a DarGlobal project record into a clean structured document."""
    title = raw_proj.get("title", "")
    brand = raw_proj.get("brand", "DarGlobal Luxury")
    city = raw_proj.get("city", "")
    country = raw_proj.get("country", "")
    prop_type = raw_proj.get("property_type", "Luxury Residences")
    price = raw_proj.get("price", "Price on Application")
    price_num = raw_proj.get("price_numeric")
    currency = raw_proj.get("currency", "AED")
    units = raw_proj.get("units", [])
    amenities = raw_proj.get("amenities", [])
    handover = raw_proj.get("handover_date", "TBA")
    desc = raw_proj.get("description", "")
    url = raw_proj.get("url", "https://darglobal.co.uk")

    desc_parts = [
        f"**{clean_text(title)}** is an ultra-luxury residential development by DarGlobal in partnership with {brand}.",
        f"Location: {city}, {country}.",
        f"Property Type: {prop_type}.",
        f"Pricing: {price}.",
        f"Units offered: {', '.join(units) if units else 'Custom residences, penthouses and villas'}.",
        f"Expected Handover: {handover}.",
        f"Amenities & Lifestyle: {', '.join(amenities) if amenities else 'World-class signature amenities'}.",
        clean_text(desc)
    ]

    return {
        "id": f"darglobal_{raw_proj.get('id', title.lower().replace(' ', '_'))}",
        "source": "DarGlobal",
        "title": clean_text(title),
        "developer_or_brand": f"DarGlobal x {brand}",
        "location": {
            "city": city,
            "district": raw_proj.get("district", city),
            "country": country,
            "lat": raw_proj.get("lat"),
            "lon": raw_proj.get("lon"),
            "address": f"{city}, {country}"
        },
        "property_type": prop_type,
        "price": price,
        "price_numeric": price_num,
        "currency": currency,
        "bedrooms": raw_proj.get("bedrooms", "1 - 5 BR"),
        "area_sqm": raw_proj.get("area_sqm", "Varies by layout"),
        "amenities": amenities,
        "handover_date": handover,
        "description": " ".join(desc_parts),
        "url": url
    }
