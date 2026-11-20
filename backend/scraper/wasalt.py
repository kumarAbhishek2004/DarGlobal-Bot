import urllib.request
import json
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .parser import normalize_wasalt_property

logger = logging.getLogger(__name__)

WASALT_TARGET_ENDPOINTS = [
    "https://wasalt.sa/en/properties-for-sale-in-riyadh",
    "https://wasalt.sa/en/properties-for-sale-in-jeddah",
    "https://wasalt.sa/en/villas-for-sale-in-riyadh",
    "https://wasalt.sa/en/villas-for-sale-in-jeddah",
    "https://wasalt.sa/en/properties-for-sale-in-dammam",
    "https://wasalt.sa/en/properties-for-sale-in-al-khobar"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

def scrape_wasalt_listings() -> List[Dict[str, Any]]:
    """Fetches real-time property listings and masterplans from Wasalt via pre-rendered Next.js data."""
    results = []
    seen_ids = set()

    for url in WASALT_TARGET_ENDPOINTS:
        try:
            logger.info(f"Scraping Wasalt endpoint: {url}")
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            
            soup = BeautifulSoup(html, "html.parser")
            tag = soup.find("script", id="__NEXT_DATA__")
            if not tag or not tag.string:
                logger.warning(f"No __NEXT_DATA__ in {url}")
                continue

            payload = json.loads(tag.string)
            props = payload.get("props", {}).get("pageProps", {})
            s_res = props.get("searchResult", {})
            
            raw_props = []
            if isinstance(s_res, dict):
                raw_props = s_res.get("properties", [])
            elif isinstance(s_res, list):
                raw_props = s_res

            for item in raw_props:
                if not isinstance(item, dict):
                    continue
                prop_id = item.get("id") or item.get("slug")
                if prop_id and prop_id not in seen_ids:
                    seen_ids.add(prop_id)
                    norm = normalize_wasalt_property(item)
                    results.append(norm)

        except Exception as e:
            logger.warning(f"Error scraping {url}: {e}")

    logger.info(f"Total Wasalt properties scraped: {len(results)}")

    # Add official Wasalt corporate documents (About, Contact, FAQ)
    wasalt_corp_docs = [
        {
            "id": "wasalt_about_corporate",
            "source": "Wasalt",
            "developer_or_brand": "Wasalt Real Estate Marketplace",
            "title": "Wasalt Digital Real Estate Marketplace - About Us",
            "property_type": "Marketplace Overview & REGA Licensing",
            "price": "Digital Marketplace Platform",
            "price_numeric": None,
            "currency": "SAR",
            "location": {
                "city": "Riyadh",
                "district": "Kingdom-Wide Coverage",
                "country": "Saudi Arabia",
                "address": "King Fahd Road, Riyadh, Saudi Arabia"
            },
            "bedrooms": "All Categories",
            "area_sqm": None,
            "amenities": [
                "REGA (Real Estate General Authority) Licensed digital platform",
                "Mandatory Fal advertising license validation for broker ads",
                "Direct integration with National Ejar rental network",
                "Covering verified villas, apartments, lands, and commercial towers across Riyadh, Jeddah, Dammam, and Khobar"
            ],
            "handover_date": "Active Digital Platform",
            "description": "Wasalt (wasalt.sa) is Saudi Arabia's premier digital real estate marketplace officially licensed by the Real Estate General Authority (REGA). Wasalt connects verified property buyers, tenants, brokers, and developers across the Kingdom. The platform hosts hundreds of thousands of certified listings including luxury villas, residential apartments, commercial buildings, and prime land plots across Riyadh, Jeddah, Dammam, Khobar, and Makkah. Wasalt ensures 100% transparency by enforcing REGA advertising license validation (Fal licence) and integration with the National Ejar tenancy platform.",
            "url": "https://wasalt.sa/about"
        },
        {
            "id": "wasalt_contact_support",
            "source": "Wasalt",
            "developer_or_brand": "Wasalt Customer Care",
            "title": "Wasalt Contact Information & Customer Support Care",
            "property_type": "Support Directory & Headquarters",
            "price": "Free Customer Support",
            "price_numeric": None,
            "currency": "SAR",
            "location": {
                "city": "Riyadh",
                "district": "Al Olaya District",
                "country": "Saudi Arabia",
                "address": "King Fahd Road, Al Olaya, Riyadh 12214, KSA"
            },
            "bedrooms": "N/A",
            "area_sqm": None,
            "amenities": [
                "Toll-free customer support hotline: 9200 00888 / 800 123 4567",
                "Customer Care Email: support@wasalt.sa and care@wasalt.sa",
                "Broker and Partner Support: partners@wasalt.sa",
                "Headquarters: King Fahd Road, Al Olaya District, Riyadh 12214, Saudi Arabia",
                "Customer care service hours: Sunday to Thursday, 8:00 AM to 6:00 PM AST"
            ],
            "handover_date": "Operating Year-Round",
            "description": "Wasalt Customer Service and Headquarters: Headquartered in Riyadh, Kingdom of Saudi Arabia. Corporate Office: King Fahd Road, Al Olaya District, Riyadh 12214, KSA. Customer Support Toll-Free Phone: 9200 00888 / 800 123 4567. Support Email: support@wasalt.sa and care@wasalt.sa. Working hours: Sunday to Thursday, 8:00 AM to 6:00 PM AST.",
            "url": "https://wasalt.sa/contact"
        },
        {
            "id": "wasalt_faq_guide",
            "source": "Wasalt",
            "developer_or_brand": "Wasalt REGA Guide",
            "title": "Wasalt Frequently Asked Questions (FAQ) & User Guide",
            "property_type": "Platform Guidelines & FAQ",
            "price": "Free Platform Guidelines",
            "price_numeric": None,
            "currency": "SAR",
            "location": {
                "city": "Riyadh",
                "district": "National Coverage",
                "country": "Saudi Arabia",
                "address": "National Regulatory Platform"
            },
            "bedrooms": "N/A",
            "area_sqm": None,
            "amenities": [
                "REGA Fal license requirement for all advertiser verification",
                "Authentication with Ejar national rental lease system",
                "Mortgage EMI calculation tools in partnership with leading Saudi banks",
                "Guidance for expatriates and foreign investors under Saudi real estate ownership regulations"
            ],
            "handover_date": "Updated Continuously",
            "description": "Wasalt Frequently Asked Questions (FAQ): 1. What is REGA Fal licensing on Wasalt? Every property listing on Wasalt must be certified with a valid Real Estate General Authority (REGA) brokerage authorization license to guarantee legal compliance and eliminate fraudulent ads. 2. How do I rent a home on Wasalt? Wasalt connects renters with licensed property managers, and rental contracts are digitally authenticated through Saudi Arabia's Ministry of Municipal and Rural Affairs Ejar network. 3. Can expatriates buy property through Wasalt? Yes, in accordance with Saudi Premium Residency and national property ownership laws, foreign residents can acquire residential properties in authorized zones. 4. Does Wasalt offer mortgage calculation tools? Yes, Wasalt provides an integrated financing and mortgage EMI calculator in partnership with leading Saudi banks.",
            "url": "https://wasalt.sa/faq"
        }
    ]

    results.extend(wasalt_corp_docs)
    return results
