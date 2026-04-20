"""
YAWEB.AI Business Scraper Service
Finds local businesses without websites (prospects) using Google Places
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import re
import unicodedata
import uuid as uuid_lib


# ============================================================================
# DATA MODELS
# ============================================================================

class Prospect(BaseModel):
    """Model for a business prospect (business without website)"""
    id: str = None
    nombre: str
    google_url: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    ciudad: str
    categoria: str
    estado: str = "nuevo"  # nuevo, contactado, convertido
    slug: str
    web_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Restaurante El Palo",
                "google_url": "https://www.google.com/maps/place/Restaurante+El+Palo",
                "direccion": "Calle Mayor 15, Madrid",
                "telefono": "+34 912 345 678",
                "whatsapp": "+34 612 345 678",
                "email": None,
                "ciudad": "Madrid",
                "categoria": "restaurante",
                "estado": "nuevo",
                "slug": "restaurante-el-palo-madrid-912345678"
            }
        }


class BusinessSearchResult(BaseModel):
    """Model for a business found in Google Places search"""
    place_id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    google_url: str
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def has_website(self) -> bool:
        """Check if the business has a website"""
        return self.website is not None and self.website.strip() != ""


# ============================================================================
# SLUG GENERATOR
# ============================================================================

def generate_slug(name: str, city: str, phone: Optional[str] = None) -> str:
    """
    Generate a URL-friendly slug for demo.yawweb.ai/{slug}

    Format: {business-name}-{city}-{last-4-phone-digits}
    Example: restaurante-el-palo-madrid-5678
    """
    # Normalize unicode characters (e.g., á -> a, ñ -> n)
    def normalize_text(text: str) -> str:
        # Normalize to NFKD form and encode to ASCII
        normalized = unicodedata.normalize('NFKD', text)
        # Remove combining characters
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        return ascii_text

    # Clean and lowercase the name
    name_slug = normalize_text(name.lower())
    # Replace spaces and special chars with hyphens
    name_slug = re.sub(r'[^a-z0-9\s-]', '', name_slug)
    name_slug = re.sub(r'[\s_]+', '-', name_slug)
    name_slug = name_slug.strip('-')

    # Clean city
    city_slug = normalize_text(city.lower())
    city_slug = re.sub(r'[^a-z0-9\s-]', '', city_slug)
    city_slug = city_slug.strip()

    # Extract last 4 digits from phone if available
    phone_suffix = ""
    if phone:
        digits = re.sub(r'\D', '', phone)
        if digits:
            phone_suffix = f"-{digits[-4:]}"

    # Build slug
    slug = f"{name_slug}-{city_slug}{phone_suffix}"
    # Remove duplicate hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug


# ============================================================================
# GOOGLE PLACES SCRAPER
# ============================================================================

class GooglePlacesScraper:
    """
    Scraper for finding local businesses without websites.
    Uses Google Places API when available, falls back to mock data for testing.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.use_mock = api_key is None or api_key == ""

    # ========================================================================
    # MOCK DATA FOR TESTING (Madrid Restaurants)
    # ========================================================================

    MOCK_BUSINESSES: List[BusinessSearchResult] = [
        BusinessSearchResult(
            place_id="mock_1",
            name="Restaurante El Palo",
            address="Calle Mayor 15, 28013 Madrid",
            phone="+34 912 345 678",
            website=None,  # NO WEBSITE - good prospect!
            google_url="https://www.google.com/maps/place/Restaurante+El+Palo",
            rating=4.3,
            reviews_count=127,
            category="restaurante",
            latitude=40.4168,
            longitude=-3.7038
        ),
        BusinessSearchResult(
            place_id="mock_2",
            name="Bar La Taza",
            address="Plaza del Sol 8, 28013 Madrid",
            phone="+34 914 567 890",
            website=None,  # NO WEBSITE - good prospect!
            google_url="https://www.google.com/maps/place/Bar+La+Taza",
            rating=4.1,
            reviews_count=89,
            category="bar",
            latitude=40.4150,
            longitude=-3.7035
        ),
        BusinessSearchResult(
            place_id="mock_3",
            name="Casa Ricardo - Tradicional",
            address="Calle Arenal 22, 28013 Madrid",
            phone="+34 915 123 456",
            website="https://casaricardo.com",  # HAS WEBSITE - not a prospect
            google_url="https://www.google.com/maps/place/Casa+Ricardo",
            rating=4.5,
            reviews_count=342,
            category="restaurante",
            latitude=40.4175,
            longitude=-3.7040
        ),
        BusinessSearchResult(
            place_id="mock_4",
            name="Pizzería Napoli",
            address="Calle Gran Via 45, 28013 Madrid",
            phone="+34 916 789 012",
            website=None,  # NO WEBSITE - good prospect!
            google_url="https://www.google.com/maps/place/Pizzer%C3%ADa+Napoli",
            rating=4.0,
            reviews_count=203,
            category="pizzeria",
            latitude=40.4190,
            longitude=-3.7055
        ),
        BusinessSearchResult(
            place_id="mock_5",
            name="Café de la Plaza",
            address="Plaza Mayor 3, 28012 Madrid",
            phone="+34 917 234 567",
            website=None,  # NO WEBSITE - good prospect!
            google_url="https://www.google.com/maps/place/Caf%C3%A9+de+la+Plaza",
            rating=4.2,
            reviews_count=156,
            category="café",
            latitude=40.4150,
            longitude=-3.7070
        ),
        BusinessSearchResult(
            place_id="mock_6",
            name="Tapas y Vinos",
            address="Calle Preciados 28, 28013 Madrid",
            phone="+34 918 345 678",
            website="https://tapasyvinos.es",  # HAS WEBSITE - not a prospect
            google_url="https://www.google.com/maps/place/Tapas+y+Vinos",
            rating=4.4,
            reviews_count=198,
            category="tapas",
            latitude=40.4160,
            longitude=-3.7045
        ),
        BusinessSearchResult(
            place_id="mock_7",
            name="Cervecería El Lobo",
            address="Calle Fuencarral 112, 28010 Madrid",
            phone="+34 919 456 789",
            website=None,  # NO WEBSITE - good prospect!
            google_url="https://www.google.com/maps/place/Cervecer%C3%ADa+El+Lobo",
            rating=3.9,
            reviews_count=67,
            category="cervecería",
            latitude=40.4280,
            longitude=-3.7010
        ),
        BusinessSearchResult(
            place_id="mock_8",
            name="Asador Txistu",
            address="Paseo de la Castellana 89, 28046 Madrid",
            phone="+34 920 567 890",
            website="https://txistu.com",  # HAS WEBSITE - not a prospect
            google_url="https://www.google.com/maps/place/Asador+Txistu",
            rating=4.6,
            reviews_count=421,
            category="asador",
            latitude=40.4350,
            longitude=-3.6890
        ),
        BusinessSearchResult(
            place_id="mock_9",
            name="Heladería San Ginés",
            address="Pasadizo de San Ginés 5, 28013 Madrid",
            phone="+34 921 678 901",
            website=None,  # NO WEBSITE - good prospect!
            google_url="https://www.google.com/maps/place/Helader%C3%ADa+San+ Gin%C3%A9s",
            rating=4.7,
            reviews_count=512,
            category="heladería",
            latitude=40.4155,
            longitude=-3.7060
        ),
        BusinessSearchResult(
            place_id="mock_10",
            name="Taberna del Volante",
            address="Calle Alcalá 85, 28009 Madrid",
            phone="+34 922 789 012",
            website=None,  # NO WEBSITE - good prospect!
            google_url="https://www.google.com/maps/place/Taberna+del+Volante",
            rating=4.0,
reviews_count=94,
            category="taberna",
            latitude=40.4220,
            longitude=-3.6680
        ),
    ]

    # ========================================================================
    # SEARCH METHODS
    # ========================================================================

    async def search_businesses(
        self,
        city: str,
        category: str,
        max_results: int = 20
    ) -> List[BusinessSearchResult]:
        """
        Search for businesses by city and category.

        Args:
            city: City name (e.g., "Madrid", "Barcelona")
            category: Business category (e.g., "restaurante", "bar", "café")
            max_results: Maximum number of results to return

        Returns:
            List of BusinessSearchResult objects
        """
        if self.use_mock:
            return self._get_mock_businesses(city, category, max_results)

        return await self._search_google_places_api(city, category, max_results)

    def _get_mock_businesses(
        self,
        city: str,
        category: str,
        max_results: int
    ) -> List[BusinessSearchResult]:
        """Get mock businesses for testing (filtered by city and category)"""
        city_lower = city.lower()
        category_lower = category.lower()

        # Filter mock businesses by city (Madrid) and category
        filtered = [
            b for b in self.MOCK_BUSINESSES
            if city_lower in b.address.lower() and
               (category_lower in b.category.lower() or category_lower == "restaurante")
        ]

        return filtered[:max_results]

    async def _search_google_places_api(
        self,
        city: str,
        category: str,
        max_results: int
    ) -> List[BusinessSearchResult]:
        """Search using Google Places API"""
        import httpx

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        query = f"{category} in {city}"
        params = {
            "query": query,
            "key": self.api_key,
            "language": "es"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") != "OK":
                    logger.warning(f"Google Places API error: {data.get('status')}")
                    return []

                businesses = []
                for result in data.get("results", [])[:max_results]:
                    place_id = result.get("place_id", "")
                    business = BusinessSearchResult(
                        place_id=place_id,
                        name=result.get("name", ""),
                        address=result.get("formatted_address"),
                        google_url=f"https://www.google.com/maps/place/{place_id}",
                        rating=result.get("rating"),
                        reviews_count=result.get("user_ratings_total"),
                        category=result.get("types", [None])[0] if result.get("types") else None,
                        latitude=result.get("geometry", {}).get("location", {}).get("lat"),
                        longitude=result.get("geometry", {}).get("location", {}).get("lng"),
                    )

                    # Get website from place details if available
                    website = await self._get_place_website(place_id)
                    business.website = website

                    businesses.append(business)

                return businesses

        except Exception as e:
            logger.error(f"Error searching Google Places: {e}")
            return []

    async def _get_place_website(self, place_id: str) -> Optional[str]:
        """Get the website URL for a specific place"""
        import httpx

        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "website",
            "key": self.api_key
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "OK":
                    return data.get("result", {}).get("website")

        except Exception:
            pass

        return None

    # ========================================================================
    # FILTERING METHODS
    # ========================================================================

    def filter_without_website(
        self,
        businesses: List[BusinessSearchResult]
    ) -> List[BusinessSearchResult]:
        """
        Filter businesses that don't have a website.
        These are the key prospects for YAWEB.AI!

        Args:
            businesses: List of business search results

        Returns:
            List of businesses without websites
        """
        return [b for b in businesses if not b.has_website()]

    def filter_by_rating(
        self,
        businesses: List[BusinessSearchResult],
        min_rating: float = 0.0
    ) -> List[BusinessSearchResult]:
        """Filter businesses by minimum rating"""
        return [
            b for b in businesses
            if b.rating is not None and b.rating >= min_rating
        ]

    def filter_by_reviews_count(
        self,
        businesses: List[BusinessSearchResult],
        min_reviews: int = 0
    ) -> List[BusinessSearchResult]:
        """Filter businesses by minimum number of reviews"""
        return [
            b for b in businesses
            if b.reviews_count is not None and b.reviews_count >= min_reviews
        ]

    # ========================================================================
    # PROSPECT CONVERSION
    # ========================================================================

    def business_to_prospect(
        self,
        business: BusinessSearchResult,
        ciudad: str,
        categoria: str
    ) -> Prospect:
        """
        Convert a BusinessSearchResult to a Prospect.

        Args:
            business: Business search result
            ciudad: City name
            categoria: Category name

        Returns:
            Prospect object ready for storage
        """
        slug = generate_slug(business.name, ciudad, business.phone)

        # Try to extract WhatsApp from phone (if it's a Spanish mobile)
        whatsapp = None
        if business.phone:
            digits = re.sub(r'\D', '', business.phone)
            # Spanish mobile numbers start with 6 or 7
            if digits.startswith('34') and len(digits) >= 11:
                if digits[2:4] in ['6', '7']:
                    whatsapp = f"+{digits}"

        prospect = Prospect(
            id=str(uuid_lib.uuid4())[:12],  # Generate unique ID
            nombre=business.name,
            google_url=business.google_url,
            direccion=business.address,
            telefono=business.phone,
            whatsapp=whatsapp,
            email=None,  # Cannot extract from Google Places
            ciudad=ciudad,
            categoria=categoria,
            estado="nuevo",
            slug=slug,
            web_id=business.place_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        return prospect

    def businesses_to_prospects(
        self,
        businesses: List[BusinessSearchResult],
        ciudad: str,
        categoria: str
    ) -> List[Prospect]:
        """
        Convert a list of businesses to prospects.

        Args:
            businesses: List of business search results
            ciudad: City name
            categoria: Category name

        Returns:
            List of Prospect objects
        """
        return [
            self.business_to_prospect(b, ciudad, categoria)
            for b in businesses
        ]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_phone_from_text(text: str) -> Optional[str]:
    """Extract phone number from text"""
    # Spanish phone patterns
    patterns = [
        r'\+34\s*(\d{3})\s*(\d{3})\s*(\d{3})',  # +34 XXX XXX XXX
        r'34\s*(\d{3})\s*(\d{3})\s*(\d{3})',    # 34 XXX XXX XXX
        r'(\d{3})\s*(\d{3})\s*(\d{3})',         # XXX XXX XXX
        r'\d{9}',                               # 9 digits
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            digits = re.sub(r'\D', '', match.group(0))
            if len(digits) == 9:
                return f"+34 {digits[:3]} {digits[3:6]} {digits[6:]}"
            elif len(digits) == 11 and digits.startswith('34'):
                return f"+{digits[0:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"

    return None


def extract_email_from_text(text: str) -> Optional[str]:
    """Extract email address from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def is_valid_phone(phone: Optional[str]) -> bool:
    """Check if a phone number is valid (Spanish format)"""
    if not phone:
        return False

    digits = re.sub(r'\D', '', phone)

    # Spanish numbers: 9 digits, optionally with +34 prefix
    if len(digits) == 9:
        return True
    if len(digits) == 11 and digits.startswith('34'):
        return True

    return False


def is_spanish_mobile(phone: Optional[str]) -> bool:
    """Check if phone is a Spanish mobile number"""
    if not phone:
        return False

    digits = re.sub(r'\D', '', phone)

    # Spanish mobile numbers start with 6 or 7
    if len(digits) == 9 and digits[0] in ['6', '7']:
        return True
    if len(digits) == 11 and digits.startswith('346') or digits.startswith('347'):
        return True

    return False


# ============================================================================
# LOGGER SETUP
# ============================================================================

import logging

logger = logging.getLogger(__name__)
