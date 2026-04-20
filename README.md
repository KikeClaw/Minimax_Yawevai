# YAWEB.AI

**Generador automático de páginas web para negocios locales usando IA.**

## 🚀 Quick Start

### Usando Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <repo-url>
cd yaweb-ai

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Iniciar servicios
docker-compose up -d
```

### Desarrollo Local

#### Backend (Python/FastAPI)

```bash
cd backend

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

#### Frontend (Next.js)

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev
```

## 📋 Requisitos

### Backend
- Python 3.11+
- OpenAI API key (opcional, usa generación mock si no está configurada)
- Google Places API key (opcional)

### Frontend
- Node.js 18+
- npm o yarn

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Backend
OPENAI_API_KEY=sk-...          # Opcional: para generación con IA
ANTHROPIC_API_KEY=sk-ant-...   # Opcional: alternativa a OpenAI
GOOGLE_PLACES_API_KEY=...       # Opcional: para extraer datos de Google
LLM_PROVIDER=openai            # openai, anthropic, o mock
DEBUG=true

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎯 Uso

### Generar una Web

1. Accede a http://localhost:3000
2. Introduce la URL de Google Business Profile (opcional)
3. Añade contexto adicional para personalizar (recomendado)
4. Haz clic en "Generar Web Ahora"
5. Descarga el ZIP o prévisualiza la web

### API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/generate` | Generar una nueva web |
| GET | `/api/webs` | Listar todas las webs |
| GET | `/api/webs/:id` | Ver detalles de una web |
| GET | `/api/webs/:id/download` | Descargar ZIP |
| GET | `/api/webs/:id/preview` | Previsualizar HTML |
| DELETE | `/api/webs/:id` | Eliminar web |

### Ejemplo CLI

```bash
# Generar web desde CLI
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "google_url": "https://www.google.com/maps/place/...",
    "context": "Bar familiar con los mejores pinchos de Valencia",
    "plan": "basic"
  }'
```

## 📁 Estructura del Proyecto

```
yaweb-ai/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Configuración
│   │   ├── models.py         # Modelos Pydantic
│   │   ├── routers/          # Endpoints API
│   │   └── services/         # Lógica de negocio
│   ├── templates/            # Templates HTML
│   ├── output/               # Webs generadas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/        # Componentes React
│   │   └── lib/              # Utilidades
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── SPEC.md
└── README.md
```

## 🎨 Webs Generadas

Cada web generada incluye:

1. **QUIENES SOMOS** - Historia y compromiso
2. **SERVICIOS** - Lista de servicios
3. **DONDE ESTAMOS** - Mapa + dirección
4. **HORARIOS** - Tabla de horarios
5. **GALERÍA** - Fotos del negocio
6. **CONTACTO** - Formulario + datos
7. **REDES SOCIALES** - Iconos y enlaces
8. **CARTA** (restaurantes) - Menú PDF

## 💰 Precios

| Plan | Primer Año | Renovación |
|------|------------|------------|
| Básico | 149€ | 49€/año |
| Premium | 395€ | 79€/año |
| LAN Plus | 750€ | 120€/año |

## 📜 Licencia

MIT License
