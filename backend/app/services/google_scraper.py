"""
Google Places Scraper Service
Uses Playwright for scraping Google Business Profile data
"""
import re
import json
import httpx
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs
from ..models import GoogleBusinessData
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class GoogleScraperService:
    """Service for extracting business data from Google Business Profile"""
    
    # Restaurant/bar categories
    RESTAURANT_CATEGORIES = [
        "restaurante", "restaurant", "bar", "café", "cafe", "taberna",
        "pizzería", "pizzeria", "comida rápida", "fast food", "burger",
        "sushi", "cevichería", "tapas", "bodega", "cervecería", "pub",
        "heladería", "heladeria", "panadería", "panaderia", "pastelería",
        "comedor", "asador", "grill"
    ]
    
    def __init__(self):
        self.use_api = settings.google_places_api_key is not None
        self.use_playwright = settings.use_playwright_scraper
    
    def extract_place_id(self, google_url: str) -> Optional[str]:
        """Extract place ID from Google Maps URL"""
        try:
            # Handle different Google Maps URL formats
            if "place/" in google_url:
                match = re.search(r'place/([^/@]+)', google_url)
                if match:
                    return match.group(1)
            
            # Handle /maps/place/ format
            if "/maps/place/" in google_url:
                parsed = urlparse(google_url)
                place_id = parse_qs(parsed.query).get('place', [None])[0]
                if place_id:
                    return place_id
            
            # Handle !3m1!1s3m1!1s... format (shortened)
            if "!3m" in google_url:
                parts = google_url.split("/")
                for i, part in enumerate(parts):
                    if part.startswith("!3m"):
                        # Extract place_id from this segment
                        match = re.search(r'!1s(.*?)!', part)
                        if match:
                            return match.group(1)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting place_id: {e}")
            return None
    
    async def fetch_from_api(self, place_id: str) -> Optional[Dict]:
        """Fetch data from Google Places API"""
        if not settings.google_places_api_key:
            return None
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "key": settings.google_places_api_key,
                "fields": "name,formatted_address,formatted_phone_number,email,opening_hours,rating,user_ratings_total,photos,website,business_status,types,url"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                data = response.json()
                
                if data.get("status") == "OK":
                    return data.get("result")
                return None
        except Exception as e:
            logger.error(f"Google Places API error: {e}")
            return None
    
    async def fetch_from_scraper(self, google_url: str) -> Optional[Dict]:
        """Fetch data using Playwright scraper (mock implementation)"""
        # In production, this would use Playwright to scrape Google Maps
        # For now, return None to trigger mock data generation
        logger.info(f"Would scrape: {google_url}")
        return None
    
    def _is_restaurant_category(self, types: List[str]) -> bool:
        """Check if business category is restaurant/bar"""
        types_lower = [t.lower() for t in types]
        for category in self.RESTAURANT_CATEGORIES:
            if category in types_lower:
                return True
        return False
    
    def _check_name_for_restaurant(self, name: str) -> bool:
        """Heuristic check if name suggests a restaurant/bar"""
        name_lower = name.lower()
        keywords = ["bar", "restaurante", "café", "cafe", "taberna", "pizzería", 
                   "burger", "sushi", "tapas", "bodega", "terraza", "cocina"]
        return any(kw in name_lower for kw in keywords)
    
    async def extract(self, google_url: str) -> Optional[GoogleBusinessData]:
        """
        Main extraction method
        Tries API first, then scraper, then returns None for manual mode
        """
        if not google_url or google_url.strip() == "":
            return None
        
        # Extract place_id
        place_id = self.extract_place_id(google_url)
        if not place_id:
            logger.warning(f"Could not extract place_id from URL: {google_url}")
            return None
        
        # Try API first
        if self.use_api:
            api_data = await self.fetch_from_api(place_id)
            if api_data:
                return self._parse_api_response(api_data)
        
        # Try scraper
        if self.use_playwright:
            scraper_data = await self.fetch_from_scraper(google_url)
            if scraper_data:
                return self._parse_scraper_response(scraper_data)
        
        # If we can't extract, return None (will use context-only mode)
        logger.info("No extraction method available, will use context-only mode")
        return None
    
    def _parse_api_response(self, data: Dict) -> GoogleBusinessData:
        """Parse Google Places API response"""
        photos = []
        if "photos" in data:
            for photo in data.get("photos", [])[:10]:
                if "photo_reference" in photo:
                    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo['photo_reference']}&key={settings.google_places_api_key}"
                    photos.append(url)
        
        hours = {}
        if "opening_hours" in data and "weekday_text" in data["opening_hours"]:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            spanish_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            for i, hours_text in enumerate(data["opening_hours"].get("weekday_text", [])):
                hours[days[i]] = hours_text
                hours[spanish_days[i]] = hours_text
        
        is_restaurant = self._is_restaurant_category(data.get("types", []))
        
        # Also check name
        if not is_restaurant and "name" in data:
            is_restaurant = self._check_name_for_restaurant(data["name"])
        
        return GoogleBusinessData(
            name=data.get("name"),
            address=data.get("formatted_address"),
            phone=data.get("formatted_phone_number"),
            email=data.get("email"),
            hours=hours,
            rating=data.get("rating"),
            reviews_count=data.get("user_ratings_total"),
            photos=photos,
            website=data.get("website"),
            social_links={},  # Google doesn't provide this
            menu_url=None,  # Would need separate extraction
            is_restaurant=is_restaurant,
            place_id=data.get("place_id")
        )
    
    def _parse_scraper_response(self, data: Dict) -> GoogleBusinessData:
        """Parse scraped data"""
        return GoogleBusinessData(
            name=data.get("name"),
            address=data.get("address"),
            phone=data.get("phone"),
            email=data.get("email"),
            hours=data.get("hours", {}),
            rating=data.get("rating"),
            reviews_count=data.get("reviews_count"),
            photos=data.get("photos", []),
            website=data.get("website"),
            social_links=data.get("social_links", {}),
            menu_url=data.get("menu_url"),
            is_restaurant=data.get("is_restaurant", False),
            place_id=data.get("place_id")
        )


# Singleton instance
google_scraper = GoogleScraperService()
