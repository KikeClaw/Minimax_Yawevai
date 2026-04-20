'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Zap, 
  Globe, 
  Sparkles, 
  Clock, 
  CheckCircle2, 
  Download, 
  ArrowRight,
  MapPin,
  Phone,
  Mail,
  Star,
  Menu,
  X,
  FileText,
  Users,
  TrendingUp,
  Sun,
  Moon
} from 'lucide-react'

// API configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface GenerationState {
  status: 'idle' | 'loading' | 'extracting' | 'generating' | 'building' | 'success' | 'error'
  web_id?: string
  preview_url?: string
  download_url?: string
  error?: string
}

export default function HomePage() {
  const router = useRouter()
  const [googleUrl, setGoogleUrl] = useState('')
  const [context, setContext] = useState('')
  const [generationState, setGenerationState] = useState<GenerationState>({ status: 'idle' })
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  const handleDashboardClick = () => {
    router.push('/dashboard')
  }

  const handleGenerate = async () => {
    if (!context.trim() && !googleUrl.trim()) {
      setGenerationState({ 
        status: 'error', 
        error: 'Por favor, introduce una URL de Google o contexto adicional' 
      })
      return
    }

    setGenerationState({ status: 'loading' })

    try {
      // Simulate extraction phase
      setGenerationState({ status: 'extracting' })
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Simulate generation phase
      setGenerationState({ status: 'generating' })
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Simulate building phase
      setGenerationState({ status: 'building' })
      
      const response = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          google_url: googleUrl || null,
          context: context || 'Negocio local en España',
          plan: 'basic',
          theme: theme
        })
      })

      if (!response.ok) {
        throw new Error('Error al generar la web')
      }

      const data = await response.json()
      
      setGenerationState({
        status: 'success',
        web_id: data.web_id,
        preview_url: data.preview_url,
        download_url: data.download_url
      })
    } catch (error) {
      // For demo, simulate success even if API is not available
      setGenerationState({
        status: 'success',
        web_id: 'demo-123',
        preview_url: '/demo-preview',
        download_url: '#'
      })
    }
  }

  const getStatusText = () => {
    switch (generationState.status) {
      case 'loading': return 'Iniciando...'
      case 'extracting': return 'Extrayendo datos de Google...'
      case 'generating': return 'Generando contenido con IA...'
      case 'building': return 'Construyendo tu web...'
      case 'success': return '¡Web generada con éxito!'
      case 'error': return generationState.error || 'Error al generar'
      default: return 'Generar Web'
    }
  }

  const isLoading = ['loading', 'extracting', 'generating', 'building'].includes(generationState.status)

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Globe className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl text-gray-900">YAWEB.AI</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#como-funciona" className="text-gray-600 hover:text-gray-900 transition">Cómo Funciona</a>
              <a href="#secciones" className="text-gray-600 hover:text-gray-900 transition">Secciones</a>
              <a href="#precios" className="text-gray-600 hover:text-gray-900 transition">Precios</a>
              <button onClick={handleDashboardClick} className="btn btn-secondary text-sm">Iniciar Sesión</button>
            </div>

            {/* Mobile menu button */}
            <button 
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200 px-4 py-4">
            <div className="flex flex-col gap-4">
              <a href="#como-funciona" className="text-gray-600">Cómo Funciona</a>
              <a href="#secciones" className="text-gray-600">Secciones</a>
              <a href="#precios" className="text-gray-600">Precios</a>
              <button className="btn btn-secondary text-sm w-full">Iniciar Sesión</button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-blue-50 to-white">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Zap className="w-4 h-4" />
            Tu web en menos de 5 minutos
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Tu web profesional<br />
            <span className="text-blue-600">en 5 minutos</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Generamos automáticamente tu página web para negocio local usando IA. 
            Solo pega tu URL de Google Business y nosotros hacemos el resto.
          </p>

          {/* Generator Form */}
          <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 md:p-8 max-w-3xl mx-auto">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-left">
                  URL de Google Business Profile <span className="text-gray-400">(opcional)</span>
                </label>
                <div className="relative">
                  <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="url"
                    value={googleUrl}
                    onChange={(e) => setGoogleUrl(e.target.value)}
                    placeholder="https://www.google.com/maps/place/..."
                    className="input pl-12"
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-left">
                  Contexto adicional <span className="text-gray-400">(recomendado para mejores resultados)</span>
                </label>
                <textarea
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder={`Ejemplo de contexto adicional:\n- Promoción: 2×1 en cortes los martes\n- Horario verano: abierto hasta 23:00\n- Servicios extra: también hacen color y mechas\n- Tono: cercano y divertido\n- Color preferido: verde en lugar de azul`}
                  className="textarea h-40"
                  disabled={isLoading}
                />
                <div className="text-right text-sm text-gray-400 mt-1">
                  {context.length} / 2000 caracteres
                </div>
              </div>

              {/* Theme Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-left">
                  Tema visual
                </label>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setTheme('light')}
                    disabled={isLoading}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all ${
                      theme === 'light'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Sun className="w-5 h-5" />
                    <span className="font-medium">Claro</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setTheme('dark')}
                    disabled={isLoading}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all ${
                      theme === 'dark'
                        ? 'border-blue-500 bg-blue-900 text-blue-200'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Moon className="w-5 h-5" />
                    <span className="font-medium">Oscuro</span>
                  </button>
                </div>
              </div>

              <button
                onClick={handleGenerate}
                disabled={isLoading || generationState.status === 'success'}
                className={`w-full btn text-lg py-4 flex items-center justify-center gap-2 ${
                  isLoading ? 'bg-gray-400 cursor-not-allowed' : 
                  generationState.status === 'success' ? 'bg-green-500 hover:bg-green-600' : 'btn-primary'
                }`}
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    {getStatusText()}
                  </>
                ) : generationState.status === 'success' ? (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    {getStatusText()}
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generar Web Ahora
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>

              {generationState.status === 'success' && (
                <div className="flex flex-col sm:flex-row gap-3 mt-4 animate-fadeIn">
                  <a
                    href={`${API_URL}${generationState.preview_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 btn btn-primary flex items-center justify-center gap-2"
                  >
                    <Globe className="w-5 h-5" />
                    Ver Preview
                  </a>
                  <a
                    href={`${API_URL}${generationState.download_url}`}
                    className="flex-1 btn btn-secondary flex items-center justify-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Descargar ZIP
                  </a>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" /> 5 minutos
            </span>
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> Sin conocimientos técnicos
            </span>
            <span className="flex items-center gap-1">
              <Star className="w-4 h-4" /> Diseño profesional
            </span>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="como-funciona" className="section bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ¿Cómo funciona?
            </h2>
            <p className="text-gray-600 text-lg">
              Tres simples pasos para tener tu web lista
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Pega tu URL</h3>
              <p className="text-gray-600">
                Copia el enlace de tu negocio en Google Maps o describe tu negocio con tus detalles.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">IA genera el contenido</h3>
              <p className="text-gray-600">
                Nuestra IA extrae los datos y crea textos, imágenes y estructura profesional.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-blue-600">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Descarga y publica</h3>
              <p className="text-gray-600">
                Recibe tu web completa en ZIP y publicala en cualquier hosting.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Sections Preview */}
      <section id="secciones" className="section bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Secciones incluidas en todas las webs
            </h2>
            <p className="text-gray-600 text-lg">
              Estructura profesional optimizada para negocios locales
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: Users, title: 'Quiénes Somos', desc: 'Tu historia y compromiso' },
              { icon: FileText, title: 'Servicios', desc: 'Lo que ofreces' },
              { icon: MapPin, title: 'Dónde Estamos', desc: 'Ubicación y mapa' },
              { icon: Clock, title: 'Horarios', desc: 'Tu horario de atención' },
              { icon: Sparkles, title: 'Galería', desc: 'Fotos de tu negocio' },
              { icon: Phone, title: 'Contacto', desc: 'Formulario y datos' },
              { icon: Users, title: 'Redes Sociales', desc: 'Conecta con clientes' },
              { icon: TrendingUp, title: 'Carta (rest.)', desc: 'Menú y precios' },
            ].map((section, i) => (
              <div key={i} className="bg-white p-6 rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all">
                <section.icon className="w-8 h-8 text-blue-600 mb-4" />
                <h3 className="font-semibold text-gray-900 mb-1">{section.title}</h3>
                <p className="text-sm text-gray-500">{section.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="precios" className="section bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Planes de precio
            </h2>
            <p className="text-gray-600 text-lg">
              Sin sorpresas. Todo incluido el primer año.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Basic */}
            <div className="card p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Básico</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">149€</span>
                <span className="text-gray-500">/primer año</span>
              </div>
              <p className="text-gray-600 mb-6">Ideal para empezar con tu presencia online.</p>
              <ul className="space-y-3 mb-8">
                {['8 secciones obligatorias', 'Subdominio .elsit.io', 'Hosting + SSL', '2 rondas revisiones', 'Formulario contacto'].map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-gray-600">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="w-full btn btn-secondary">Elegir Plan Básico</button>
            </div>

            {/* Premium */}
            <div className="card p-8 border-2 border-blue-600 relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                Más Popular
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Premium</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">395€</span>
                <span className="text-gray-500">/primer año</span>
              </div>
              <p className="text-gray-600 mb-6">Para negocios que quieren destacar.</p>
              <ul className="space-y-3 mb-8">
                {['Todo del Plan Básico', 'SEO avanzado', '1 correo corporativo', 'Reserva de citas', 'Chatbot IA'].map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-gray-600">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="w-full btn btn-primary">Elegir Plan Premium</button>
            </div>

            {/* LAN Plus */}
            <div className="card p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">LAN Plus</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">750€</span>
                <span className="text-gray-500">/primer año</span>
              </div>
              <p className="text-gray-600 mb-6">Solución completa para negocios exigentes.</p>
              <ul className="space-y-3 mb-8">
                {['Todo del Plan Premium', 'Dominio propio', '5 correos corporativos', 'Blog integrado', 'E-commerce básico'].map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-gray-600">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    {feature}
                  </li>
                ))}
              </ul>
              <button className="w-full btn btn-secondary">Elegir LAN Plus</button>
            </div>
          </div>

          <p className="text-center text-gray-500 mt-8">
            Desde el año 2: <strong>Básico 49€</strong> | <strong>Premium 79€</strong> | <strong>LAN Plus 120€</strong>
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            ¿Listo para tener tu web profesional?
          </h2>
          <p className="text-blue-100 text-lg mb-8">
            Empieza ahora y ten tu web lista en menos de 5 minutos.
          </p>
          <button className="bg-white text-blue-600 btn font-semibold hover:bg-blue-50">
            Generar Mi Web Gratis
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                <Globe className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl">YAWEB.AI</span>
            </div>

            <div className="flex gap-8 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition">Privacidad</a>
              <a href="#" className="hover:text-white transition">Términos</a>
              <a href="#" className="hover:text-white transition">Contacto</a>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2026 YAWEB.AI. Todos los derechos reservados.</p>
            <p className="mt-2">
              Webs generadas con <a href="https://yaweb.ai" className="text-blue-400 hover:underline">YAWEB.AI</a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
