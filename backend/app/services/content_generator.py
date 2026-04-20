"""
AI Content Generator Service
Uses LLM to generate web content from extracted data or context
Supports: OpenAI, Anthropic, Google Gemini, MiniMax
"""
import json
import re
import os
from typing import Optional, Dict, Any, List
from ..models import GoogleBusinessData, GeneratedContent
from ..config import settings
import logging

logger = logging.getLogger(__name__)


# Category colors mapping
CATEGORY_COLORS = {
    "barbería": "#1e3a8a",  # Azul oscuro
    "barber": "#1e3a8a",
    "restaurante": "#ea580c",  # Naranja
    "restaurant": "#ea580c",
    "café": "#f59e0b",  # Ámbar
    "cafe": "#f59e0b",
    "bar": "#f59e0b",
    "fontanero": "#059669",  # Verde
    "plumber": "#059669",
    "peluquería": "#db2777",  # Rosa
    "peluqueria": "#db2777",
    "salon": "#db2777",
    "default": "#3b82f6"  # Azul genérico
}


def get_color_for_category(category: str) -> str:
    """Get primary color based on business category"""
    category_lower = category.lower()
    for key, color in CATEGORY_COLORS.items():
        if key in category_lower:
            return color
    return CATEGORY_COLORS["default"]


def get_tone_from_context(context: str) -> str:
    """Extract tone preference from context"""
    if "divertido" in context.lower() or "familiar" in context.lower():
        return "divertido y familiar"
    elif "formal" in context.lower():
        return "formal y elegante"
    elif "cercano" in context.lower():
        return "cercano y personal"
    return "profesional y cercano"


def _filter_reviews(reviews: List[Dict], min_rating: int = 4) -> List[Dict]:
    """Filter reviews to only include those with rating >= min_rating"""
    if not reviews:
        return []
    filtered = [r for r in reviews if r.get('rating', 0) >= min_rating]
    return filtered[:6]  # Max 6 reviews


def _smart_truncate(text: str, max_length: int = 200) -> str:
    """Truncate text at sentence boundaries, not mid-sentence"""
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    # Find the last period or comma as sentence boundary
    last_period = truncated.rfind('.')
    last_comma = truncated.rfind(',')
    last_boundary = max(last_period, last_comma)
    
    # Only truncate if we found a good boundary (at least 60% of max_length)
    if last_boundary > max_length * 0.6:
        return text[:last_boundary + 1]
    
    return truncated + '...'


def _format_whatsapp_number(phone: str) -> str:
    """Format phone number for WhatsApp with Spanish +34 prefix"""
    if not phone:
        return phone
    
    # Remove spaces, dashes, dots, parentheses
    clean = re.sub(r'[\s\-\.\(\)]', '', phone)
    
    # Spanish mobile numbers (6 or 7 followed by 8 digits)
    if re.match(r'^[67]\d{8}$', clean):
        return f'+34{clean}'
    
    # Already has 34 but missing +
    if re.match(r'^34[67]\d{8}$', clean):
        return f'+{clean}'
    
    # International format already (starts with +)
    if phone.startswith('+'):
        return phone
    
    return phone


def generate_mock_content(google_data: Optional[GoogleBusinessData], context: str, category: str = "negocio local") -> GeneratedContent:
    """Generate content using simple rules when no LLM is available"""
    
    # Extract basic info
    name = google_data.name if google_data else "Tu Negocio"
    address = google_data.address if google_data else "Dirección no disponible"
    phone = google_data.phone if google_data else "Teléfono no disponible"
    rating = google_data.rating if google_data else 4.5
    reviews_count = google_data.reviews_count if google_data else 0
    
    # Check if restaurant
    is_restaurant = False
    if google_data:
        is_restaurant = google_data.is_restaurant
    else:
        # Infer from context
        restaurant_keywords = ["restaurante", "bar", "café", "taberna", "pizzería", "comida", "pizzas", "tapas"]
        is_restaurant = any(kw in context.lower() for kw in restaurant_keywords)
    
    # Extract color
    primary_color = get_color_for_category(category)
    
    # Infer category from context
    if "barbería" in context.lower() or "barber" in context.lower():
        category = "barbería"
        primary_color = "#1e3a8a"
    elif "peluquer" in context.lower():
        category = "peluquería"
        primary_color = "#db2777"
    elif "fontaner" in context.lower() or "plomber" in context.lower():
        category = "fontanería"
        primary_color = "#059669"
    elif "restaurante" in context.lower() or "bar" in context.lower():
        category = "bar/restaurante"
        primary_color = "#ea580c"
    elif "café" in context.lower() or "cafe" in context.lower():
        category = "cafetería"
        primary_color = "#f59e0b"
    
    # Try to infer color from context
    if "verde" in context.lower():
        primary_color = "#059669"
    elif "rojo" in context.lower():
        primary_color = "#dc2626"
    elif "azul" in context.lower() and "barber" not in context.lower():
        primary_color = "#2563eb"
    elif "naranja" in context.lower():
        primary_color = "#ea580c"
    elif "rosa" in context.lower():
        primary_color = "#db2777"
    elif "morado" in context.lower():
        primary_color = "#7c3aed"
    
    # Determine tone
    tone = get_tone_from_context(context)
    
    # Generate about text
    about_templates = [
        f"Somos {name}, un {category} comprometido con la satisfacción de nuestros clientes. "
        f"Con una valoración de {rating}/5 basada en {reviews_count} opiniones, nos esforzamos "
        f"por ofrecer el mejor servicio. "
        f"Te esperamos para demostrate por qué nuestros clientes nos eligen día tras día."
    ]
    
    if "bar" in context.lower() or "tapas" in context.lower():
        address_part = address.split(',')[0] if address and ',' in address else "el centro"
        about_templates = [
            f"Somos {name}, un espacio {tone} donde cada visita se siente como estar en casa. "
            f"Disfruta de nuestros productos cuidadosamente seleccionados en {address_part}. "
            f"¡Salud y bienvenidos!"
        ]
    
    # Extract custom Quiénes Somos from context
    if "QUIENES SOMOS" in context.upper() or "quienes somos" in context.lower():
        match = re.search(r'(?:QUIENES SOMOS|quienes somos)[:\s]+([^\n]+(?:\n[^\n]+)*)', context, re.IGNORECASE)
        if match:
            about_text = match.group(1).strip()[:300]
        else:
            about_text = about_templates[0]
    else:
        about_text = about_templates[0]
    
    # Generate services
    default_services = [
        "Servicio de atención al cliente",
        "Presupuestos sin compromiso",
        "Trabajo garantizado",
        "Respuesta rápida",
        "Profesionales cualificados",
        "Mejor precio garantizado"
    ]
    
    if "color" in context.lower() and "mechas" in context.lower():
        default_services = ["Corte", "Color", "Mechas", "Peinados", "Tratamientos capilares", "Asesoramiento personalizado"]
    elif "bar" in category.lower() or "restaurante" in category.lower():
        default_services = ["Menú del día", "Carta", "Reservas", "Terraza", "Catering", "Eventos privados"]
    elif "barbería" in category.lower():
        default_services = ["Corte clásico", "Arreglo de barba", "Afeitado tradicional", "Tratamiento facial", "Tintura", "Paquete completo"]
    
    # Try to extract services from context
    if "servicios" in context.lower() or "servicio" in context.lower():
        services_match = re.search(r'(?:servicios?|servicio)[:\s]+([^\n]+(?:\n[^\n-]+)*)', context, re.IGNORECASE)
        if services_match:
            services_text = services_match.group(1)
            services = [s.strip() for s in re.split(r'[,;•\n]', services_text) if s.strip()]
            if len(services) >= 3:
                default_services = services[:6]
    
    # Generate hours table
    hours_html = """
    <table class="hours-table">
        <tr><td>Lunes</td><td>9:00 - 20:00</td></tr>
        <tr><td>Martes</td><td>9:00 - 20:00</td></tr>
        <tr><td>Miércoles</td><td>9:00 - 20:00</td></tr>
        <tr><td>Jueves</td><td>9:00 - 20:00</td></tr>
        <tr><td>Viernes</td><td>9:00 - 21:00</td></tr>
        <tr><td>Sábado</td><td>10:00 - 14:00</td></tr>
        <tr><td>Domingo</td><td>Cerrado</td></tr>
    </table>
    """
    
    # Extract special hours from context
    if "verano" in context.lower() and "23:00" in context:
        hours_html = hours_html.replace("21:00", "23:00")
    if "cerrado" in context.lower():
        hours_html = hours_html.replace("<tr><td>Domingo</td><td>Cerrado</td></tr>", "<tr><td>Domingo</td><td>Cerrado</td></tr>")
    
    # Generate SEO content
    city_part = address.split(',')[-1].strip() if address and ',' in address else "tu zona"
    reviews_text = f"con {rating} estrellas" if rating else ""
    seo_title = f"{name} | {category.title()} en {city_part}"
    if len(seo_title) > 60:
        seo_title = f"{name} | {category.title()} profesional"
    
    seo_description = f"{name} - {category.title()} {reviews_text}. "
    if address:
        seo_description += f"Encuéntranos en {address.split(',')[0]}. "
    seo_description += "Visítanos o contacta ahora."
    if len(seo_description) > 160:
        seo_description = f"{name} - {category.title()} profesional {reviews_text}. Solicita información sin compromiso."
    
    # CTA text
    cta_text = "Contacta ahora"
    if is_restaurant or "bar" in category.lower():
        cta_text = "Reserva tu mesa"
    elif "barbería" in category.lower():
        cta_text = "Pide tu cita"
    elif "promoción" in context.lower() or "2x1" in context.lower() or "2×1" in context.lower():
        cta_text = "¡Aprovecha la oferta!"
    
    # Subtitle
    subtitle = f"{category.title()} profesional en {city_part}"
    if rating:
        subtitle += f" • ⭐ {rating}/5 ({reviews_count} reseñas)"
    
    # Title
    title = name
    
    # Social links
    social_links: Dict[str, Optional[str]] = {}
    if google_data and google_data.social_links:
        social_links = google_data.social_links
    else:
        # Check context for social links
        if "instagram" in context.lower():
            social_links["instagram"] = "https://instagram.com/"
        if "facebook" in context.lower():
            social_links["facebook"] = "https://facebook.com/"
        if "tiktok" in context.lower():
            social_links["tiktok"] = "https://tiktok.com/@"
    
    # Generate testimonials from reviews (filter >= 4 stars)
    testimonials = []
    if google_data and google_data.reviews:
        filtered_reviews = _filter_reviews(google_data.reviews, min_rating=4)
        testimonials = [
            {
                "name": r.get("author", "Cliente"),
                "rating": r.get("rating", 5),
                "text": _smart_truncate(r.get("text", ""), max_length=200),
                "date": r.get("date", "")
            }
            for r in filtered_reviews
        ]
    
    return GeneratedContent(
        title=title,
        subtitle=subtitle,
        about_text=about_text,
        services=default_services,
        cta_text=cta_text,
        primary_color=primary_color,
        opening_hours_html=hours_html,
        seo_title=seo_title,
        seo_description=seo_description,
        social_links=social_links,
        menu_pdf_url=None,
        is_restaurant_bar=is_restaurant,
        testimonials=testimonials
    )


class ContentGeneratorService:
    """Service for generating web content using AI - Multi-provider support"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.use_llm = False
        self.client = None
        self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client based on provider"""
        self.use_llm = False
        self.client = None
        
        if self.provider == "openai" and settings.openai_api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                self.use_llm = True
                logger.info(f"Initialized OpenAI client with model {self.model}")
            except ImportError:
                logger.warning("OpenAI not installed, using mock generation")
                self.use_llm = False
                
        elif self.provider == "anthropic" and settings.anthropic_api_key:
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
                self.use_llm = True
                logger.info(f"Initialized Anthropic client with model {self.model}")
            except ImportError:
                logger.warning("Anthropic not installed, using mock generation")
                self.use_llm = False
                
        elif self.provider == "google" and settings.google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.google_api_key)
                self.client = genai
                self.use_llm = True
                logger.info(f"Initialized Google Gemini client with model {self.model}")
            except ImportError:
                logger.warning("Google GenerativeAI not installed, using mock generation")
                self.use_llm = False
            except Exception as e:
                logger.warning(f"Failed to initialize Google Gemini: {e}")
                self.use_llm = False
                
        elif self.provider == "minimax" and settings.minimax_api_key:
            self.use_llm = True
            logger.info(f"Initialized MiniMax client with model {self.model}")
            # MiniMax uses HTTP requests directly
            
        else:
            self.use_llm = False
            logger.info("Using mock content generation (no LLM API key configured)")
    
    async def generate(self, google_data: Optional[GoogleBusinessData], context: str) -> GeneratedContent:
        """Generate content - uses LLM if available, otherwise mock"""
        
        # Detect category
        category = "negocio local"
        if google_data:
            category = "restaurante" if google_data.is_restaurant else "servicio local"
        
        # Try LLM first
        if self.use_llm:
            try:
                content = await self._generate_with_llm(google_data, context)
                if content:
                    return content
            except Exception as e:
                logger.error(f"LLM generation failed: {e}, falling back to mock")
        
        # Fallback to mock generation
        return generate_mock_content(google_data, context, category)
    
    async def _generate_with_llm(self, google_data: Optional[GoogleBusinessData], context: str) -> Optional[GeneratedContent]:
        """Generate content using LLM API - Supports all providers"""
        
        # Detect category
        category = "negocio local"
        if google_data and google_data.is_restaurant:
            category = "restaurante"
        
        # Infer from context
        if "barbería" in context.lower() or "barber" in context.lower():
            category = "barbería"
        elif "peluquer" in context.lower():
            category = "peluquería"
        elif "fontaner" in context.lower():
            category = "fontanería"
        elif "restaurante" in context.lower():
            category = "restaurante"
        elif "café" in context.lower() or "cafe" in context.lower():
            category = "café"
        elif "bar" in context.lower():
            category = "bar"
        
        tone = get_tone_from_context(context)
        
        # Get data safely
        name = google_data.name if google_data else "Tu Negocio"
        address = google_data.address if google_data else "No disponible"
        phone = google_data.phone if google_data else "No disponible"
        rating = google_data.rating if google_data else 0
        reviews = google_data.reviews_count if google_data else 0
        
        prompt = f"""Eres un copywriter profesional de negocios locales en España.
Tu tarea: Crear contenido para una web one-page con secciones FIJAS.

DATOS:
- Nombre: {name}
- Categoría: {category}
- Dirección: {address}
- Teléfono: {phone}
- Reseñas: {rating}/5 ({reviews} opiniones)
- Contexto adicional: {context}

INSTRUCCIONES:
1. Genera SOLO JSON válido, sin markdown ni texto adicional
2. Todos los textos en ESPAÑOL
3. about_text: 80-120 palabras, tono {tone}
4. services: 6 servicios relevantes
5. opening_hours_html: tabla HTML con días en español
6. primary_color: color hex apropiado para {category}
7. is_restaurant_bar: true si es restaurante/bar/café

Responde SOLO con este JSON:
{{
  "title": "...",
  "subtitle": "...",
  "about_text": "...",
  "services": ["...", "..."],
  "cta_text": "...",
  "primary_color": "#...",
  "opening_hours_html": "<table>...</table>",
  "seo_title": "...",
  "seo_description": "...",
  "social_links": {{"instagram": null, "facebook": null, "tiktok": null}},
  "menu_pdf_url": null,
  "is_restaurant_bar": true/false
}}"""

        content = None
        
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            content = response.choices[0].message.content
            
        elif self.provider == "anthropic":
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text
            
        elif self.provider == "google":
            # Google Gemini synchronous call
            try:
                model = self.client.GenerativeModel(self.model)
                response = model.generate_content(prompt)
                content = response.text
            except Exception as e:
                logger.error(f"Google Gemini error: {e}")
                return None
                
        elif self.provider == "minimax":
            # MiniMax API call
            content = await self._call_minimax(prompt)
            
        else:
            return None
        
        if not content:
            return None
        
        # Parse JSON response
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        
        try:
            data = json.loads(content)
            return GeneratedContent(**data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return None
    
    async def _call_minimax(self, prompt: str) -> Optional[str]:
        """Call MiniMax API"""
        try:
            import aiohttp
            
            url = "https://api.minimax.chat/v1/text/chatcompletion_pro"
            headers = {
                "Authorization": f"Bearer {settings.minimax_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, timeout=60) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    else:
                        error_text = await response.text()
                        logger.error(f"MiniMax API error: {response.status} - {error_text}")
                        return None
        except ImportError:
            logger.warning("aiohttp not installed, cannot use MiniMax API")
            return None
        except Exception as e:
            logger.error(f"MiniMax API error: {e}")
            return None


# Singleton instance
content_generator = ContentGeneratorService()
