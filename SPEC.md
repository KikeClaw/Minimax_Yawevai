# YAWEB.AI - Especificación Técnica MVP

## 1. Concepto & Visión

**YAWEB.AI** es una herramienta SaaS que genera automáticamente páginas web estáticas profesionales para negocios locales en España. Utiliza IA para extraer datos de Google Business Profile y generar una web one-page completa con menú fijo de secciones específicas en menos de 5 minutos.

**Personalidad de marca:**
- Velocidad: "Tu web en 5 minutos"
- Profesionalismo local: Enfocado en negocios españoles
- Simplicidad: Sin conocimientos técnicos requeridos
- Precio transparente: Sin sorpresas

---

## 2. Modelo de Negocio Dual

### Modelo A — Landing Pública (B2C directo)

El cliente llega a **yaweb.ai**, genera una preview de su web de forma gratuita y puede activarla pagando 99€.

**Flujo completo:**
1. Cliente visita yaweb.ai
2. Introduce URL de Google Business o contexto textual
3. IA genera preview de la web (sin descarga ZIP)
4. Ve banner de activación: **"Actívala ahora por 99€"**
5. Paga con Stripe (checkout integrado)
6. En minutos: su web queda publicada en `tunegocio.yaweb.ai`
7. Recibe email con credenciales y enlace a su web

### Modelo B — Dashboard Interno (B2B / Resellers)

Un vendedor o agencia usa el dashboard interno para prospectar negocios sin web y cerrar ventas de forma outbound.

**Flujo completo:**
1. Scraper busca ~200 negocios locales sin web activa
2. El sistema auto-genera 200 demos publicadas en `demo.yaweb.ai/{slug}`
3. Se envía WhatsApp/email masivo personalizado al negocio ("Hemos creado una demo de tu web")
4. Vendedor contacta → muestra demo → cierra venta
5. Activa la web para el cliente → se publica en `tunegocio.yaweb.ai`
6. Vendedor recibe comisión por venta cerrada

---

## 3. Design Language

### Aesthetic Direction
Diseño corporativo moderno con toques mediterráneos. Inspirado en Stripe y Linear pero con colores cálidos españoles.

### Color Palette
```css
--primary: #2563eb;        /* Azul corporativo */
--primary-dark: #1d4ed8;   /* Azul hover */
--secondary: #f59e0b;      /* Ámbar - accents */
--success: #10b981;        /* Verde éxito */
--error: #ef4444;          /* Rojo errores */
--background: #ffffff;     /* Fondo principal */
--surface: #f8fafc;        /* Superficie cards */
--text-primary: #0f172a;  /* Texto principal */
--text-secondary: #64748b; /* Texto secundario */
--border: #e2e8f0;         /* Bordes */
```

### Category Colors (para las webs generadas)
```css
--barberia: #1e3a8a;       /* Azul oscuro */
--restaurante: #ea580c;    /* Naranja */
--cafe-bar: #f59e0b;       /* Ámbar */
--fontanero: #059669;      /* Verde */
--peluqueria: #db2777;     /* Rosa */
--default: #3b82f6;        /* Azul genérico */
```

### Typography
- **Headings:** Inter (700, 600)
- **Body:** Inter (400, 500)
- **Mono:** JetBrains Mono (código)
- **Fallbacks:** system-ui, -apple-system, sans-serif

### Spatial System
- Base unit: 4px
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96
- Border radius: 8px (cards), 6px (buttons), 4px (inputs)
- Max content width: 1280px

### Motion Philosophy
- Micro-interactions: 150ms ease-out
- Page transitions: 300ms ease-in-out
- Loading states: skeleton shimmer animation
- Success feedback: checkmark animation

---

## 4. Layout & Structure

### Landing Pública (Modelo A)

```
┌─────────────────────────────────────────────────────────┐
│  HEADER (sticky)                                        │
│  Logo yaweb.ai | Cómo funciona | Precio | Contacto     │
├─────────────────────────────────────────────────────────┤
│  HERO SECTION                                           │
│  H1: "Tu web profesional en 5 minutos"│
│  Subtitle + CTA principal                               │
├─────────────────────────────────────────────────────────┤
│  GENERADOR (campo principal)                            │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ URL Google Business  │ │ Contexto Adicional   │     │
│  │ (opcional)           │ │ (textarea)           │     │
│  └──────────────────────┘ └──────────────────────┘     │
│  [ Generar Preview Gratis ]                             │
├─────────────────────────────────────────────────────────┤
│  PREVIEW GENERADA                                       │
│  iframe / render de la web generada                     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  BANNER ACTIVACIÓN                               │  │
│  │  "Tu web está lista. Actívala ahora por 99€"     │  │
│  │  [ Activar y Publicar — 99€ ]  (Stripe)          │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  CÓMO FUNCIONA (3 pasos)                               │
│  1. Introduce tu negocio → 2. IA genera → 3. Publica   │
├─────────────────────────────────────────────────────────┤
│  PRECIO ÚNICO                                           │
│  99€ primer año · 49€/año a partir del segundo         │
├─────────────────────────────────────────────────────────┤
│  FOOTER                                                 │
│  Links | Legal | © 2026 YAWEB.AI                       │
└─────────────────────────────────────────────────────────┘
```

### Dashboard Interno (Modelo B — Admin/Vendedor)

```
┌──────────────┬──────────────────────────────────────────┐
│ SIDEBAR      │  HEADER                                  │
│              ├──────────────────────────────────────────┤
│ Dashboard    │  MAIN CONTENT (tabs)                     │
│ Scraper      ││
│ Demos        │  [Scraper] [Demos] [Ventas] [Webs Live]  │
│ Webs Live    │                                          │
│ Ventas       │  - Lista negocios encontrados            │
│ Ajustes      │  - Estado de cada demo (generada/enviada)│
│              │  - Botón "Activar web" por cliente       │
│              │  - Comisiones registradas                │
└──────────────┴──────────────────────────────────────────┘
```

### Responsive Strategy
- **Mobile first:** Stack vertical en <768px
- **Tablet:** 2 columnas en 768-1024px
- **Desktop:** Layout completo en >1024px

---

## 5. Features & Interactions

### 5.1 Generador de Web (Core Feature)

#### Inputs
1. **URL Google Business Profile** (opcional)
   - Placeholder: `https://www.google.com/maps/place/...`
   - Validación: debe ser URL válida de Google Maps
   - Feedback: icono de check cuando es válida

2. **Contexto Adicional** (obligatorio si no hay URL)
   - Textarea con placeholder instructivo
   - Límite: 2000 caracteres
   - Contador de caracteres en tiempo real

#### Lógica de Procesamiento
```
IF url_google_business IS NOT EMPTY:
    datos_auto = extraer_de_google_business(url)
    IF contexto IS NOT EMPTY:
        datos_finales = fusionar(datos_auto, contexto)
    ELSE:
        datos_finales = datos_auto
ELSE:
    IF contexto IS NOT EMPTY:
        datos_finales = generar_desde_cero(contexto)
    ELSE:
        mostrar_error("Debe proporcionar URL o contexto")
```

#### Estados de UI
- **Idle:** Formulario visible, botón "Generar Preview Gratis"
- **Loading:** Spinner + "Extrayendo datos de Google..." (5s)
- **Processing:** "Generando contenido con IA..." (10s)
- **Building:** "Construyendo tu web..." (3s)
- **Success:** Preview de la web + banner de activación (99€)
- **Error:** Mensaje de error específico + retry

### 5.2 Extracción Google Business (Backend)

#### Datos a Extraer
- `name` - Nombre del negocio
- `formatted_address` - Dirección completa
- `formatted_phone_number` - Teléfono
- `opening_hours.weekday_text` - Horarios
- `rating` / `user_ratings_total` - Reseñas
- `photos` - URLs de 5-10 fotos
- `website` - Web existente
- `business_status` - Estado activo/cerrado
- `place_id` - ID único Google

#### Métodos de Extracción
1. **Google Places API** (preferido si hay API key)
2. **Scraping con Playwright** (fallback)

### 5.3 Generación de Contenido IA

#### Prompt para LLM
```
Eres un copywriter profesional de negocios locales en España.
Genera contenido para una web one-page con estas secciones FIJAS:

DATOS: {datos_extraidos_o_contexto}
CATEGORÍA: {categoria_inferida}

Responde SOLO con JSON válido:
{
  "title": "...",
  "subtitle": "...",
  "about_text": "...",
  "services": [...],
  "cta_text": "...",
  "primary_color": "...",
  "opening_hours_html": "...",
  "seo_title": "...",
  "seo_description": "...",
  "social_links": {...},
  "is_restaurant_bar": true/false
}
```

### 5.4 Construcción de Web Estática

#### Template HTML (secciones fijas — 8 secciones)
```html
<nav class="fixed top-0">
  <a href="#quienes-somos">QUIENES SOMOS</a>
  <a href="#servicios">SERVICIOS</a>
  <a href="#donde-estamos">DONDE ESTAMOS</a>
  <a href="#horarios">HORARIOS</a>
  <a href="#galeria">GALERÍA</a>
  <a href="#contacto">CONTACTO</a>
  <a href="#redes">REDES</a>
  <!-- + CARTA si restaurante -->
</nav>

<header id="hero">...</header>
<section id="quienes-somos">...</section>
<section id="servicios">...</section>
<section id="donde-estamos">...</section>
<section id="horarios">...</section>
<section id="galeria">...</section>
<section id="contacto">...</section>   <!-- Formulario de contacto -->
<section id="redes">...</section>
<!-- + CARTA si restaurante -->
<footer>...</footer>
```

#### Output (sin ZIP para el usuario final)
- Web publicada directamente en `tunegocio.yaweb.ai` al activar
- Preview interna en `preview.yaweb.ai/{web_id}` durante el proceso

### 5.5 Flujo de Activación y Pago (Modelo A)

1. Usuario ve preview generada
2. Hace clic en "Activar y Publicar — 99€"
3. Se abre Stripe Checkout (hosted o embedded)
4. Stripe confirma el pago → webhook dispara activación
5. Backend asigna subdominio `tunegocio.yaweb.ai`
6. Se envía email con enlace y credenciales (via EmailJS o Resend)
7. Web queda publicada y accesible

### 5.6 Scraper + Outreach (Modelo B)

#### Scraper de Negocios
- Busca negocios locales sin web en Google Maps por categoría y zona
- Filtra los que no tienen dominio propio activo
- Guarda resultados en Supabase: nombre, teléfono, email, dirección, categoría

#### Auto-generación de Demos
- Por cada negocio encontrado, genera web automáticamente
- Publica en `demo.yaweb.ai/{slug}` (slug derivado del nombre)
- Estado: `demo_generated`, `outreach_sent`, `sold`, `activated`

#### Outreach Masivo
- Plantilla de WhatsApp/email personalizada con link a la demo
- Seguimiento de estado de contacto por negocio

#### Panel del Vendedor
- Ver lista de negocios con demos generadas
- Marcar como "contactado", "interesado", "vendido"
- Botón "Activar Web" para publicar definitivamente en `tunegocio.yaweb.ai`
- Registro de comisiones

---

## 6. Component Inventory

### 6.1 Buttons
| Variant | Default | Hover | Disabled | Loading |
|---------|---------|-------|----------|---------| 
| Primary | bg-blue-600 text-white | bg-blue-700 | bg-gray-300 cursor-not-allowed | spinner |
| Secondary | bg-white border text-blue-600 | bg-blue-50 | bg-gray-100 | spinner |
| Ghost | text-blue-600 | bg-blue-50 | text-gray-400 | spinner |
| Activation | bg-amber-500 text-white | bg-amber-600 | — | spinner |

### 6.2 Inputs
| State | Appearance |
|-------|------------|
| Default | border-gray-300, shadow-sm |
| Focus | border-blue-500, ring-2 ring-blue-200 |
| Error | border-red-500, ring-2 ring-red-200 |
| Disabled | bg-gray-100, cursor-not-allowed |

### 6.3 Cards
- Background: white
- Border: 1px solid #e2e8f0
- Border radius: 8px
- Shadow: sm (hover: md)
- Padding: 24px

### 6.4 Activation Banner
- Background: amber-50 with amber-400 border
- Prominent CTA button
- Price displayed clearly (99€)
- Positioned below preview, sticky on scroll

### 6.5 Loading States
- Skeleton: pulse animation
- Spinner: border-spinner
- Progress bar: indeterminate for long tasks

### 6.6 Toast Notifications
- Position: bottom-right
- Auto-dismiss: 5s
- Types: success (green), error (red), info (blue)

---

## 7. Technical Approach

### Stack
```
Backend:
├── FastAPI (Python 3.11+)
├── Uvicorn (ASGI server)
├── Playwright (Google scraping)
├── OpenAI/Anthropic (LLM API)
├── Supabase (database + auth)
└── Stripe (payments)

Frontend:
├── Next.js 14 (App Router)
├── TypeScript
├── TailwindCSS
├── Lucide React (icons)
└── Framer Motion (animations)

Services:
├── Stripe — payment processing & webhooks
├── Supabase — PostgreSQL database, auth, storage
├── EmailJS / Resend — transactional email notifications
└── Cloudflare / Vercel — subdomain routing (*.yaweb.ai)

Infrastructure:
├── Docker + Docker Compose
├── Vercel (frontend)
└── Railway/Render (backend)
```

### API Endpoints

#### POST /api/generate
```typescript
// Request
{
  google_url?: string;
  context: string;
}

// Response
{
  success: boolean;
  web_id: string;
  preview_url: string;  // preview.yaweb.ai/{web_id}
}
```

#### POST /api/scraper/scan
```typescript
// Request
{
  category: string;       // "restaurante", "barberia", etc.
  location: string;       // "Madrid, Vallecas"
  limit?: number;         // default 200
}

// Response
{
  success:boolean;
  businesses_found: number;
  scan_id: string;
}
```

#### POST /api/webs/{id}/activate
```typescript
// Request
{
  subdomain: string;      // "tunegocio" → tunegocio.yaweb.ai
  customer_email: string;
  stripe_payment_id: string;
}

// Response
{
  success: boolean;
  live_url: string;       // tunegocio.yaweb.ai
}
```

#### POST /api/payments/create
```typescript
// Request
{
  web_id: string;
  subdomain: string;
  customer_email: string;
}

// Response
{
  checkout_url: string;   // Stripe hosted checkout URL
  session_id: string;
}
```

### Data Models

```typescript
interface GeneratedWeb {
  id: string;
  slug: string;
  name: string;
  category: string;
  google_url?: string;
  context: string;
  extracted_data?: GoogleBusinessData;
  generated_content?: GeneratedContent;
  preview_url: string;
  live_url?: string;             // set after activation
  status: "preview" | "demo" | "active";
  stripe_payment_id?: string;
  customer_email?: string;
  created_at: Date;
  activated_at?: Date;
}

interface Business {
  id: string;
  name: string;
  address: string;
  phone?: string;
  email?: string;
  category: string;
  google_place_id?: string;
  has_website: boolean;
  demo_url?: string;             // demo.yaweb.ai/{slug}
  outreach_status: "pending" | "contacted" | "interested" | "sold" | "rejected";
  web_id?: string;               // linked GeneratedWeb after activation
  notes?: string;
  created_at: Date;
}

interface GoogleBusinessData {
  name: string;
  address: string;
  phone: string;
  hours: Record<string, string>;
  rating?: number;
  reviews_count?: number;
  photos: string[];
  is_restaurant: boolean;
}

interface GeneratedContent {
  title: string;
  subtitle: string;
  about_text: string;
  services: string[];
  cta_text: string;
  primary_color: string;
  opening_hours_html: string;
  seo_title: string;
  seo_description: string;
  social_links: Record<string, string | null>;
  is_restaurant_bar: boolean;
}
```

### File Structure
```
/workspace/yaweb-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings + env vars
│   │   ├── models.py            # Pydantic models
│   │   ├── routers/
│   │   │   ├── generate.py      # POST /api/generate
│   │   │   ├── scraper.py       # POST /api/scraper/scan
│   │   │   ├── activate.py      # POST /api/webs/{id}/activate
│   │   │   └── payments.py      # POST /api/payments/create
│   │   └── services/
│   │       ├── google_scraper.py
│   │       ├── content_generator.py
│   │       ├── web_builder.py
│   │       ├── stripe_service.py
│   │       ├── email_service.py
│   │       └── subdomain_service.py
│   ├── templates/
│   │   └── web-template.html
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Landing pública
│   │   │   ├── layout.tsx
│   │   │   ├── globals.css
│   │   │   ├── preview/[id]/
│   │   │   │   └── page.tsx          # Preview + banner activación
│   │   │   └── admin/
│   │   │       ├── page.tsx          # Dashboard interno
│   │   │       ├── scraper/page.tsx
│   │   │       ├── demos/page.tsx
│   │   │       └── ventas/page.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── GeneratorForm.tsx
│   │   │   ├── ActivationBanner.tsx
│   │   │   ├── PricingSection.tsx
│   │   │   ├── ScraperPanel.tsx
│   │   │   └── BusinessTable.tsx
│   │   └── lib/
│   │       ├── api.ts
│   │       ├── stripe.ts
│   │       └── utils.ts
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── docker-compose.yml
└── README.md
```

---

## 8. Precio — Plan Único (Fase 1)

### Plan Básico

| | |
|---|---|
| **Precio inicial** | 99€ primer año |
| **Renovación** | 49€/año a partir del segundo |
| **Hosting** | Incluido |
| **SSL** | Incluido |
| **Subdominio** | tunegocio.yaweb.ai |
| **Secciones** | 8 secciones + CARTA si restaurante |
| **Formulario contacto** | Incluido |
| **Email de bienvenida** | Incluido |

> Planes adicionales (Premium, dominio propio, multi-página) se añadirán en Fase 2.

---

## 9. Estados y Edge Cases

### Generación
| Caso | Comportamiento |
|------|----------------|
| URL vacía + contexto vacío | Error: "Proporciona URL o contexto" |
| URL inválida | Error: "URL no válida" |
| Google Places no encontrado | Usar solo contexto, warning |
| Fallo extracción fotos | Usar stock photos genéricas |
| LLM timeout | Retry automático 2x, luego error |
| Generación exitosa | Guardar preview en Supabase, retornar preview_url |

### Pago y Activación
| Caso | Comportamiento |
|------|----------------|
| Stripe pago exitoso | Webhook activa web, envía email |
| Stripe pago fallido | Mostrar error, no activar |
| Subdominio ya en uso | Sugerir alternativa (tunegocio2.yaweb.ai) |
| Email no enviado | Reintentar 3x, log en Supabase |

### Scraper (Modelo B)
| Caso | Comportamiento |
|------|----------------|
| Negocio ya tiene web | Excluir del listado |
| Negocio ya en BD | No duplicar, actualizar datos |
| Error generando demo | Marcar como `error`, notificar admin |

---

## 10. Roadmap

### Fase 1 (Ahora)
- Landing pública con generador + preview + banner activación
- Dashboard admin con Scraper + gestión de demos
- Outreach masivo (WhatsApp/email)
- Stripe payment integration
- Hosting en subdominios yaweb.ai
- Email notifications tras activación
- Supabase como base de datos y auth

### Fase 2
- Multi-plan support (Premium / Pro)
- Custom domain mapping (dominio propio del cliente)
- User accounts / portal self-service
- SEO avanzado (schema.org, sitemap, GA4)
- Panel de analíticas básicas por web
