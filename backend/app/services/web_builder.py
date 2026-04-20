"""
Web Builder Service
Generates static HTML websites from content
"""
import os
import zipfile
import shutil
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from ..models import GeneratedContent, GoogleBusinessData
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class WebBuilderService:
    """Service for building static websites"""
    
    def __init__(self):
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_nav_items(self, content: GeneratedContent) -> str:
        """Generate navigation menu items"""
        items = [
            '<a href="#quienes-somos">QUIENES SOMOS</a>',
            '<a href="#servicios">SERVICIOS</a>',
            '<a href="#donde-estamos">DONDE ESTAMOS</a>',
            '<a href="#horarios">HORARIOS</a>',
            '<a href="#galeria">GALERÍA</a>',
            '<a href="#contacto">CONTACTO</a>',
            '<a href="#redes">REDES</a>'
        ]
        
        # Add Carta section for restaurants
        if content.is_restaurant_bar:
            items.insert(4, '<a href="#carta">CARTA</a>')
        
        return '\n    '.join(items)
    
    def _get_services_html(self, services: list) -> str:
        """Generate services section HTML"""
        services_html = ""
        for i, service in enumerate(services):
            icon = self._get_service_icon(i)
            services_html += f"""
                <div class="service-card">
                    <div class="service-icon">{icon}</div>
                    <h3>{service}</h3>
                </div>
            """
        return services_html
    
    def _get_service_icon(self, index: int) -> str:
        """Get icon for service based on index"""
        icons = [
            '<svg class="icon" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
            '<svg class="icon" viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
            '<svg class="icon" viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>',
            '<svg class="icon" viewBox="0 0 24 24"><path d="M21 10.12h-6.78l2.74-2.82c-2.73-2.7-7.15-2.8-9.88-.1-2.73 2.71-2.73 7.08 0 9.79s7.15 2.71 9.88 0C18.32 15.65 19 14.08 19 12.1h2c0 1.98-.88 4.55-2.64 6.29-3.51 3.48-9.21 3.48-12.72 0-3.5-3.47-3.53-9.11-.02-12.58s9.14-3.47 12.65 0L21 3v7.12z"/></svg>',
            '<svg class="icon" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8h16v10zm-2-1h-6v-2h6v2zM7 17v-2h10v2H7z"/></svg>',
            '<svg class="icon" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'
        ]
        return icons[index % len(icons)]
    
    def _get_placeholder_images(self, count: int = 8) -> list:
        """Get placeholder image URLs (using picsum for demo)"""
        images = []
        categories = ["food", "interior", "cafe", "restaurant", "business", "store", "office", "building"]
        for i in range(count):
            width = 800
            height = 600
            seed = 100 + i
            images.append(f"https://picsum.photos/seed/{seed}/{width}/{height}")
        return images
    
    def _get_carta_section(self, menu_url: Optional[str]) -> str:
        """Generate carta/menu section for restaurants"""
        if menu_url:
            carta_content = f'''
        <a href="{menu_url}" target="_blank" class="btn-carta">
            <svg class="icon" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
            Ver Carta Completa
        </a>
            '''
        else:
            carta_content = '''
        <div class="carta-placeholder">
            <svg class="icon-large" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/><path d="M14 2v6h6"/></svg>
            <p>Carta próximamente disponible</p>
            <span>Contacta con nosotros para más información sobre nuestro menú</span>
        </div>
            '''
        
        return f'''
    <!-- CARTA -->
    <section id="carta" class="section carta-section">
        <h2>Nuestra Carta</h2>
        <p class="section-subtitle">Descubre nuestra selección de productos y servicios</p>
        <div class="carta-container">
            {carta_content}
        </div>
    </section>
        '''
    
    def _get_social_icons(self, social_links: Dict[str, str]) -> str:
        """Generate social media icons HTML"""
        icons_html = ""
        
        social_networks = {
            "instagram": {"name": "Instagram", "path": 'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 3.27.072 3.667.072 4.947 0 3.278-.073 4.678-.072 4.948 0 3.252-1.691 4.771-4.919 4.919-3.266.058-3.646.072-4.85.072-3.204 0-3.584-.014-4.85-.072-3.271-.148-4.771-1.691-4.919-4.919-.058-3.267-.072-3.667-.072-4.947 0-3.278.073-4.678.072-4.948.148-3.252 1.691-4.771 4.919-4.919 3.266-.058 3.646-.072 4.85-.072zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z'},
            "facebook": {"name": "Facebook", "path": 'M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z'},
            "tiktok": {"name": "TikTok", "path": 'M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z'},
            "twitter": {"name": "Twitter/X", "path": 'M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z'},
            "youtube": {"name": "YouTube", "path": 'M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z'}
        }
        
        for network, data in social_networks.items():
            url = social_links.get(network)
            if url:
                icons_html += f'''
            <a href="{url}" target="_blank" class="social-icon" title="{data['name']}" aria-label="{data['name']}">
                <svg viewBox="0 0 24 24">{data['path']}</svg>
            </a>
                '''
        
        return icons_html if icons_html else ""
    
    def _generate_html(self, content: GeneratedContent, google_data: Optional[GoogleBusinessData]) -> str:
        """Generate complete HTML page"""
        
        current_year = datetime.now().year
        
        # Get images for gallery
        if google_data and google_data.photos:
            gallery_images = google_data.photos[:8]
        else:
            gallery_images = self._get_placeholder_images(8)
        
        gallery_html = ""
        for i, img_url in enumerate(gallery_images):
            gallery_html += f'''
                <div class="gallery-item">
                    <img src="{img_url}" alt="Galería {i+1}" loading="lazy">
                </div>
            '''
        
        # Social links
        social_icons = self._get_social_icons(content.social_links)
        
        # Nav items
        nav_items = self._get_nav_items(content)
        
        # Carta section for restaurants
        carta_section = self._get_carta_section(content.menu_pdf_url) if content.is_restaurant_bar else ""
        
        # Get contact info
        contact_info = {
            "address": google_data.address if google_data else "Dirección disponible próximamente",
            "phone": google_data.phone if google_data else "Teléfono disponible próximamente",
            "email": google_data.email if google_data else "info@tunegocio.es"
        }
        
        # Extract city for map
        city = contact_info["address"].split(",")[-1].strip() if contact_info["address"] else "Madrid"
        map_url = f"https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q={city},Spain&zoom=15"
        
        # Primary color with variations
        primary = content.primary_color
        primary_light = self._lighten_color(primary, 0.8)
        primary_dark = self._darken_color(primary, 0.2)
        
        html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.seo_title}</title>
    <meta name="description" content="{content.seo_description}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{content.title}">
    <meta property="og:description" content="{content.seo_description}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{gallery_images[0] if gallery_images else ''}">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --primary: {primary};
            --primary-light: {primary_light};
            --primary-dark: {primary_dark};
            --text: #1f2937;
            --text-light: #6b7280;
            --bg: #ffffff;
            --bg-light: #f9fafb;
            --border: #e5e7eb;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            color: var(--text);
            background: var(--bg);
            line-height: 1.6;
        }}
        
        /* Navigation */
        nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            z-index: 1000;
            padding: 0 2rem;
        }}
        
        nav .nav-container {{
            max-width: 1280px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 64px;
        }}
        
        .nav-brand {{
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--primary);
            text-decoration: none;
        }}
        
        nav .nav-links {{
            display: flex;
            gap: 0.5rem;
        }}
        
        nav .nav-links a {{
            color: var(--text);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        nav .nav-links a:hover {{
            background: var(--primary-light);
            color: var(--primary);
        }}
        
        .nav-toggle {{
            display: none;
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
        }}
        
        /* Hero */
        .hero {{
            padding: 8rem 2rem 4rem;
            background: linear-gradient(135deg, var(--primary-light) 0%, var(--bg) 100%);
            text-align: center;
        }}
        
        .hero h1 {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 700;
            color: var(--text);
            margin-bottom: 1rem;
        }}
        
        .hero .subtitle {{
            font-size: 1.25rem;
            color: var(--text-light);
            max-width: 600px;
            margin: 0 auto 2rem;
        }}
        
        .hero .cta-button {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .hero .cta-button:hover {{
            background: var(--primary-dark);
            transform: translateY(-2px);
        }}
        
        /* Sections */
        .section {{
            padding: 5rem 2rem;
            max-width: 1280px;
            margin: 0 auto;
        }}
        
        .section h2 {{
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
            color: var(--text);
        }}
        
        .section .section-subtitle {{
            text-align: center;
            color: var(--text-light);
            margin-bottom: 3rem;
        }}
        
        /* Services */
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }}
        
        .service-card {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.2s;
        }}
        
        .service-card:hover {{
            border-color: var(--primary);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .service-icon {{
            width: 48px;
            height: 48px;
            margin: 0 auto 1rem;
            color: var(--primary);
        }}
        
        .service-icon svg {{
            width: 100%;
            height: 100%;
        }}
        
        .service-card h3 {{
            font-size: 1.125rem;
            font-weight: 600;
        }}
        
        /* Location */
        .location-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            align-items: start;
        }}
        
        .location-info {{
            padding: 2rem;
        }}
        
        .location-info .info-item {{
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        
        .location-info .info-icon {{
            width: 24px;
            height: 24px;
            color: var(--primary);
            flex-shrink: 0;
            margin-top: 0.25rem;
        }}
        
        .location-info h3 {{
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-light);
            margin-bottom: 0.25rem;
        }}
        
        .location-info p {{
            font-size: 1rem;
        }}
        
        .map-container {{
            border-radius: 12px;
            overflow: hidden;
            height: 300px;
        }}
        
        .map-container iframe {{
            width: 100%;
            height: 100%;
            border: 0;
        }}
        
        /* Hours */
        .hours-table {{
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
            border-collapse: collapse;
        }}
        
        .hours-table tr {{
            border-bottom: 1px solid var(--border);
        }}
        
        .hours-table td {{
            padding: 1rem;
        }}
        
        .hours-table td:last-child {{
            text-align: right;
            font-weight: 500;
        }}
        
        /* Gallery */
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }}
        
        .gallery-item {{
            border-radius: 12px;
            overflow: hidden;
            aspect-ratio: 4/3;
        }}
        
        .gallery-item img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }}
        
        .gallery-item:hover img {{
            transform: scale(1.05);
        }}
        
        /* Contact */
        .contact-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
        }}
        
        .contact-info {{
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}
        
        .contact-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .contact-icon {{
            width: 48px;
            height: 48px;
            background: var(--primary-light);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
        }}
        
        .contact-form {{
            background: var(--bg-light);
            padding: 2rem;
            border-radius: 12px;
        }}
        
        .form-group {{
            margin-bottom: 1rem;
        }}
        
        .form-group label {{
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }}
        
        .form-group input,
        .form-group textarea {{
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
        }}
        
        .form-group textarea {{
            min-height: 120px;
            resize: vertical;
        }}
        
        .submit-btn {{
            width: 100%;
            background: var(--primary);
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .submit-btn:hover {{
            background: var(--primary-dark);
        }}
        
        /* Carta */
        .carta-section {{
            background: var(--bg-light);
        }}
        
        .carta-container {{
            text-align: center;
            padding: 2rem;
        }}
        
        .btn-carta {{
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            background: var(--primary);
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .btn-carta:hover {{
            background: var(--primary-dark);
            transform: translateY(-2px);
        }}
        
        .carta-placeholder {{
            padding: 3rem;
        }}
        
        .icon-large {{
            width: 64px;
            height: 64px;
            color: var(--primary);
            margin-bottom: 1rem;
        }}
        
        .carta-placeholder p {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .carta-placeholder span {{
            color: var(--text-light);
        }}
        
        /* Social */
        .social-section {{
            background: var(--primary);
            color: white;
            text-align: center;
        }}
        
        .social-section h2 {{
            color: white;
        }}
        
        .social-icons {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }}
        
        .social-icon {{
            width: 48px;
            height: 48px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            transition: all 0.2s;
        }}
        
        .social-icon:hover {{
            background: white;
            color: var(--primary);
            transform: translateY(-3px);
        }}
        
        .social-icon svg {{
            width: 24px;
            height: 24px;
        }}
        
        /* Footer */
        footer {{
            background: #111827;
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        
        footer .footer-content {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        
        footer p {{
            color: #9ca3af;
            margin-bottom: 1rem;
        }}
        
        footer a {{
            color: var(--primary-light);
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .nav-links {{
                display: none;
            }}
            
            .nav-toggle {{
                display: block;
            }}
            
            .location-content,
            .contact-content {{
                grid-template-columns: 1fr;
            }}
            
            .section {{
                padding: 3rem 1rem;
            }}
            
            .hero {{
                padding: 6rem 1rem 3rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav>
        <div class="nav-container">
            <a href="#" class="nav-brand">{content.title}</a>
            <div class="nav-links">
                {nav_items}
            </div>
            <button class="nav-toggle" aria-label="Menu">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 12h18M3 6h18M3 18h18"/>
                </svg>
            </button>
        </div>
    </nav>

    <!-- Hero -->
    <header class="hero" id="inicio">
        <h1>{content.title}</h1>
        <p class="subtitle">{content.subtitle}</p>
        <a href="#contacto" class="cta-button">{content.cta_text}</a>
    </header>

    <!-- QUIENES SOMOS -->
    <section id="quienes-somos" class="section">
        <h2>Quiénes Somos</h2>
        <p class="section-subtitle">Conoce nuestra historia y compromiso</p>
        <div style="max-width: 800px; margin: 0 auto; text-align: center;">
            <p style="font-size: 1.125rem; line-height: 1.8;">{content.about_text}</p>
        </div>
    </section>

    <!-- SERVICIOS -->
    <section id="servicios" class="section" style="background: var(--bg-light);">
        <h2>Nuestros Servicios</h2>
        <p class="section-subtitle">Lo que podemos ofrecerte</p>
        <div class="services-grid">
            {self._get_services_html(content.services)}
        </div>
    </section>

    <!-- DONDE ESTAMOS -->
    <section id="donde-estamos" class="section">
        <h2>Dónde Estamos</h2>
        <p class="section-subtitle">Te esperamos para atenderte</p>
        <div class="location-content">
            <div class="location-info">
                <div class="info-item">
                    <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                        <circle cx="12" cy="10" r="3"/>
                    </svg>
                    <div>
                        <h3>Dirección</h3>
                        <p>{contact_info["address"]}</p>
                    </div>
                </div>
                <div class="info-item">
                    <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                    </svg>
                    <div>
                        <h3>Teléfono</h3>
                        <p><a href="tel:{contact_info["phone"].replace(' ', '')}">{contact_info["phone"]}</a></p>
                    </div>
                </div>
            </div>
            <div class="map-container">
                <iframe src="{map_url}" allowfullscreen loading="lazy"></iframe>
            </div>
        </div>
    </section>

    <!-- HORARIOS -->
    <section id="horarios" class="section" style="background: var(--bg-light);">
        <h2>Horarios</h2>
        <p class="section-subtitle">Consulta nuestros horarios de atención</p>
        {content.opening_hours_html}
    </section>

    <!-- GALERÍA -->
    <section id="galeria" class="section">
        <h2>Galería</h2>
        <p class="section-subtitle">Descubre nuestro espacio</p>
        <div class="gallery-grid">
            {gallery_html}
        </div>
    </section>

    <!-- CONTACTO -->
    <section id="contacto" class="section" style="background: var(--bg-light);">
        <h2>Contacto</h2>
        <p class="section-subtitle">Ponte en contacto con nosotros</p>
        <div class="contact-content">
            <div class="contact-info">
                <div class="contact-item">
                    <div class="contact-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                            <polyline points="22,6 12,13 2,6"/>
                        </svg>
                    </div>
                    <div>
                        <strong>Email</strong>
                        <p><a href="mailto:{contact_info["email"]}">{contact_info["email"]}</a></p>
                    </div>
                </div>
                <div class="contact-item">
                    <div class="contact-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                        </svg>
                    </div>
                    <div>
                        <strong>Teléfono</strong>
                        <p><a href="tel:{contact_info["phone"].replace(' ', '')}">{contact_info["phone"]}</a></p>
                    </div>
                </div>
                <div class="contact-item">
                    <div class="contact-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                        </svg>
                    </div>
                    <div>
                        <strong>Dirección</strong>
                        <p>{contact_info["address"]}</p>
                    </div>
                </div>
            </div>
            <form class="contact-form" action="https://formspree.io/f/{{form_id}}" method="POST">
                <div class="form-group">
                    <label for="name">Nombre</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="message">Mensaje</label>
                    <textarea id="message" name="message" required></textarea>
                </div>
                <button type="submit" class="submit-btn">Enviar mensaje</button>
            </form>
        </div>
    </section>

    <!-- REDES SOCIALES -->
    <section id="redes" class="section social-section">
        <h2>Síguenos</h2>
        <p class="section-subtitle">Mantente conectado con nosotros</p>
        <div class="social-icons">
            {social_icons if social_icons else '<p style="color: rgba(255,255,255,0.7);">Redes sociales próximamente</p>'}
        </div>
    </section>

    <!-- CARTA (solo restaurantes) -->
    {carta_section}

    <!-- Footer -->
    <footer>
        <div class="footer-content">
            <p>&copy; {current_year} {content.title}. Todos los derechos reservados.</p>
            <p>
                <a href="#">Política de Privacidad</a> | 
                <a href="#">Términos y Condiciones</a>
            </p>
            <p style="margin-top: 1rem; font-size: 0.875rem;">
                Web creada con <a href="https://yaweb.ai" target="_blank">YAWEB.AI</a>
            </p>
        </div>
    </footer>

    <script>
        // Mobile menu toggle
        document.querySelector('.nav-toggle')?.addEventListener('click', function() {{
            const navLinks = document.querySelector('.nav-links');
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
            navLinks.style.flexDirection = 'column';
            navLinks.style.position = 'absolute';
            navLinks.style.top = '64px';
            navLinks.style.left = '0';
            navLinks.style.right = '0';
            navLinks.style.background = 'white';
            navLinks.style.padding = '1rem';
            navLinks.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.1)';
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def _lighten_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Lighten a hex color"""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r = int(min(255, r + (255 - r) * factor))
            g = int(min(255, g + (255 - g) * factor))
            b = int(min(255, b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#f3f4f6"
    
    def _darken_color(self, hex_color: str, factor: float = 0.2) -> str:
        """Darken a hex color"""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r = int(r * (1 - factor))
            g = int(g * (1 - factor))
            b = int(b * (1 - factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#1e40af"
    
    async def build(
        self, 
        content: GeneratedContent, 
        google_data: Optional[GoogleBusinessData],
        web_id: str
    ) -> Dict[str, Any]:
        """Build the static website"""
        
        # Create web directory
        web_dir = self.output_dir / web_id
        web_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML
        html = self._generate_html(content, google_data)
        
        # Save HTML file
        html_path = web_dir / "index.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        # Create ZIP archive
        zip_path = self.output_dir / f"{web_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(html_path, "index.html")
        
        # Get file size
        zip_size = zip_path.stat().st_size
        
        return {
            "web_id": web_id,
            "html_path": str(html_path),
            "zip_path": str(zip_path),
            "zip_size": zip_size,
            "preview_url": f"/preview/{web_id}"
        }


# Singleton instance
web_builder = WebBuilderService()
