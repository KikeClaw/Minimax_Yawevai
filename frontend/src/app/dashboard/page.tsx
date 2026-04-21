'use client';

import { useState, useEffect } from 'react';
import {
  Search,
  Users,
  FileText,
  MessageSquare,
  Globe,
  Eye,
  Play,
  Download,
  Check,
  X,
  ChevronDown,
  Send,
  Loader2,
  LayoutDashboard,
  Scissors,
  Wrench,
  ChefHat,
  Coffee,
  Building2,
  RefreshCw,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  Zap,
  Settings,
  Key,
  Bot,
  Sparkles,
  Save,
  TestTube,
  Wand2,
  Copy,
  History,
  Palette,
  Sun,
  Moon,
  Type,
  AlignJustify,
  Link,
  CopyPlus,
} from 'lucide-react';

// Types
interface Prospect {
  id: string;
  nombre: string;
  ciudad: string;
  telefono: string;
  whatsapp?: string;
  slug: string;
  estado: 'nuevo' | 'demo' | 'sent' | 'interested' | 'active';
  created_at: string;
}

interface GeneratedWeb {
  id: string;
  nombre: string;
  plan: string;
  slug: string;
  created_at: string;
  preview_url: string;
  estado: 'pending' | 'active' | 'cancelled';
}

interface ScraperResult {
  id: string;
  nombre: string;
  ciudad: string;
  telefono: string;
  slug: string;
  estado: 'nuevo' | 'demo' | 'sent' | 'interested' | 'active';
  selected: boolean;
}

interface Stats {
  total_scans: number;
  prospects_found: number;
  demos_generated: number;
  whatsapp_sent: number;
}

// AI Settings Types
interface AIModel {
  id: string;
  name: string;
  description: string;
  supports_vision: boolean;
  cost_per_generation_usd: number;
  input_cost_per_1m_tokens: number;
  output_cost_per_1m_tokens: number;
}

interface AIProvider {
  id: string;
  name: string;
  has_api_key: boolean;
  models: AIModel[];
}

interface AIConfig {
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
}

// Constants
const API_BASE_URL = 'http://localhost:8000';

const CATEGORIAS = [
  { value: 'restaurante', label: 'Restaurante', icon: ChefHat },
  { value: 'bar', label: 'Bar', icon: Coffee },
  { value: 'cafe', label: 'Cafeteria', icon: Coffee },
  { value: 'peluqueria', label: 'Peluqueria', icon: Scissors },
  { value: 'fontanero', label: 'Fontanero', icon: Wrench },
  { value: 'cerrador', label: 'Cerrador', icon: Building2 },
];

const WHATSAPP_TEMPLATES = [
  {
    id: 'demo_intro',
    name: 'Introduccion Demo',
    template: 'Hola {nombre}! Soy de YAWEB.AI. Hemos creado una web gratuita para {negocio} en {ciudad}. Puedes verla aqui: {demo_url}\n\n¿Te gusta? Podemos activarla por solo 99€/año. ¡Contesta para más info!',
  },
  {
    id: 'follow_up',
    name: 'Seguimiento',
    template: 'Hola {nombre}! Queríamos saber si pudiste ver la demo de web para {negocio}. ¿Tienes alguna pregunta?\n\nRecuerda que la primera web cuesta solo 99€/año.',
  },
  {
    id: 'activation_offer',
    name: 'Oferta Activacion',
    template: '¡{nombre}! Tu web en {demo_url} está lista. Por tiempo limitado, activación por solo 99€/año (luego 49€/año).\n\n¿Te la activamos ya?',
  },
];

// Web Creator Types
interface WebCreatorConfig {
  google_business_url: string;
  contexto_adicional: string;
  email: string;
  telefono: string;
  whatsapp: string;
  modelo_ia: string;
  tema: 'claro' | 'oscuro';
  estilo: 'moderno' | 'clasico';
  tono: 'cercano' | 'formal';
  densidad: 'completo' | 'minimo';
  color_primario: string;
}

interface GenerationHistory {
  id: string;
  nombre: string;
  slug: string;
  created_at: string;
  preview_url: string;
  config: Partial<WebCreatorConfig>;
}

interface GenerationStep {
  step: number;
  title: string;
  description: string;
}

// Web Creator Constants
const WEB_BUILDER_STEPS: GenerationStep[] = [
  { step: 1, title: 'URL Google Business', description: 'Pega la URL de tu ficha de Google Business para extraer datos automáticamente' },
  { step: 2, title: 'Datos de Contacto', description: 'Configura la información de contacto que aparecerá en la web' },
  { step: 3, title: 'Configuración IA', description: 'Selecciona el modelo de IA que generará el contenido' },
  { step: 4, title: 'Estilo y Diseño', description: 'Personaliza el tema visual, tono y densidad del contenido' },
  { step: 5, title: 'Generar Web', description: 'Inicia la generación y descarga tu web lista' },
];

const AI_MODELS_FOR_WEB = [
  { id: 'mock', name: 'Demo (Gratis)', cost: '0€', description: 'Contenido de ejemplo' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', cost: '~0.01€', description: 'Rápido y económico' },
  { id: 'gpt-4o', name: 'GPT-4o', cost: '~0.03€', description: 'Mejor calidad/precio' },
  { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', cost: '~0.04€', description: 'Excelente para contenido' },
  { id: 'gemini-1.5-flash', name: 'Gemini Flash', cost: '~0.001€', description: 'Ultra económico' },
];

const TEMA_COLORS = {
  claro: { bg: 'bg-white', text: 'text-gray-900', accent: 'from-blue-500 to-blue-600' },
  oscuro: { bg: 'bg-gray-900', text: 'text-white', accent: 'from-purple-500 to-indigo-600' },
};

const ESTADO_COLORS = {
  nuevo: 'bg-blue-100 text-blue-800',
  demo: 'bg-green-100 text-green-800',
  sent: 'bg-yellow-100 text-yellow-800',
  interested: 'bg-emerald-100 text-emerald-800',
  active: 'bg-green-800 text-white',
};

// Components
const Sidebar = ({ activeSection, setActiveSection }: { activeSection: string; setActiveSection: (s: string) => void }) => {
  const menuItems = [
    { id: 'stats', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'scraper', label: 'Scraper', icon: Search },
    { id: 'creator', label: 'Creador de Webs', icon: Wand2 },
    { id: 'prospects', label: 'Prospectos', icon: Users },
    { id: 'whatsapp', label: 'WhatsApp', icon: MessageSquare },
    { id: 'webs', label: 'Webs Creadas', icon: Globe },
    { id: 'ai-settings', label: 'AI Settings', icon: Sparkles },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen fixed left-0 top-0 flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Zap className="w-8 h-8 text-blue-500" />
          YAWEB.AI
        </h1>
        <p className="text-gray-400 text-sm mt-1">Admin Dashboard</p>
      </div>
      <nav className="flex-1 p-4">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveSection(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
              activeSection === item.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            }`}
          >
            <item.icon className="w-5 h-5" />
            {item.label}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
            <span className="font-semibold">AD</span>
          </div>
          <div>
            <p className="font-medium">Admin</p>
            <p className="text-gray-400 text-sm">admin@yaweb.ai</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

const StatsCards = ({ stats }: { stats: Stats }) => {
  const cards = [
    { label: 'Total Scans', value: stats.total_scans, icon: Search, color: 'bg-blue-500' },
    { label: 'Prospects Found', value: stats.prospects_found, icon: Users, color: 'bg-green-500' },
    { label: 'Demos Generated', value: stats.demos_generated, icon: FileText, color: 'bg-purple-500' },
    { label: 'WhatsApp Sent', value: stats.whatsapp_sent, icon: MessageSquare, color: 'bg-green-600' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card) => (
        <div key={card.label} className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">{card.label}</p>
              <p className="text-3xl font-bold mt-1">{card.value}</p>
            </div>
            <div className={`${card.color} p-3 rounded-lg`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

const ScraperSection = ({ onProspectCreated }: { onProspectCreated: () => void }) => {
  const [ciudad, setCiudad] = useState('');
  const [categoria, setCategoria] = useState('restaurante');
  const [cantidad, setCantidad] = useState(200);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ScraperResult[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/scraper/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ciudad, categoria, cantidad }),
      });
      const data = await response.json();
      setResults(
        data.map((item: any) => ({
          ...item,
          selected: false,
        }))
      );
      setSearched(true);
    } catch (error) {
      console.error('Scraper error:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id: string) => {
    setResults((prev) =>
      prev.map((r) => (r.id === id ? { ...r, selected: !r.selected } : r))
    );
  };

  const toggleSelectAll = () => {
    const allSelected = results.every((r) => r.selected);
    setResults((prev) => prev.map((r) => ({ ...r, selected: !allSelected })));
  };

  const handleGenerateDemo = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/api/demos/generate/${id}`, { method: 'POST' });
      setResults((prev) =>
        prev.map((r) => (r.id === id ? { ...r, estado: 'demo' as const } : r))
      );
      onProspectCreated();
    } catch (error) {
      console.error('Demo generation error:', error);
    }
  };

  const handleSendWhatsApp = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/api/whatsapp/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prospect_id: id }),
      });
      setResults((prev) =>
        prev.map((r) => (r.id === id ? { ...r, estado: 'sent' as const } : r))
      );
      onProspectCreated();
    } catch (error) {
      console.error('WhatsApp error:', error);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
      <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <Search className="w-5 h-5" />
        Scraper de Negocios
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ciudad</label>
          <input
            type="text"
            value={ciudad}
            onChange={(e) => setCiudad(e.target.value)}
            placeholder="Madrid, Barcelona..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
          <select
            value={categoria}
            onChange={(e) => setCategoria(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {CATEGORIAS.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Cantidad</label>
          <input
            type="number"
            value={cantidad}
            onChange={(e) => setCantidad(parseInt(e.target.value))}
            min={1}
            max={500}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="flex items-end">
          <button
            onClick={handleSearch}
            disabled={loading || !ciudad}
            className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            {loading ? 'Buscando...' : 'Buscar Negocios'}
          </button>
        </div>
      </div>

      {searched && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={results.every((r) => r.selected)}
                    onChange={toggleSelectAll}
                    className="rounded"
                  />
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nombre</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Ciudad</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Telefono</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Slug</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Estado</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {results.map((result) => (
                <tr key={result.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={result.selected}
                      onChange={() => toggleSelect(result.id)}
                      className="rounded"
                    />
                  </td>
                  <td className="px-4 py-3 font-medium">{result.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{result.ciudad}</td>
                  <td className="px-4 py-3 text-gray-600">{result.telefono}</td>
                  <td className="px-4 py-3 text-blue-600 text-sm">
                    demo.yaweb.ai/{result.slug}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${ESTADO_COLORS[result.estado]}`}>
                      {result.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button className="p-1 text-gray-600 hover:text-blue-600" title="Ver">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleGenerateDemo(result.id)}
                        className="p-1 text-gray-600 hover:text-green-600"
                        title="Generar Demo"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleSendWhatsApp(result.id)}
                        className="p-1 text-gray-600 hover:text-green-600"
                        title="WhatsApp"
                      >
                        <MessageSquare className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {results.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No se encontraron negocios. Intenta con otros parametros.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ProspectsTable = () => {
  const [filter, setFilter] = useState<'todos' | 'nuevo' | 'demo' | 'sent' | 'interested' | 'active'>('todos');
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProspects = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/prospects`);
      const data = await response.json();
      setProspects(data);
    } catch (error) {
      console.error('Fetch prospects error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProspects();
  }, []);

  const filteredProspects = filter === 'todos'
    ? prospects
    : prospects.filter((p) => p.estado === filter);

  const tabs = ['todos', 'nuevo', 'demo', 'sent', 'interested', 'active'] as const;

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Users className="w-5 h-5" />
          Prospectos
        </h2>
        <button
          onClick={fetchProspects}
          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded-lg"
          title="Actualizar"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      <div className="flex gap-2 mb-6 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              filter === tab
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            <span className="ml-2 bg-white/20 px-2 py-0.5 rounded-full text-xs">
              {tab === 'todos' ? prospects.length : prospects.filter((p) => p.estado === tab).length}
            </span>
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nombre</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Ciudad</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Telefono</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">WhatsApp</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Estado</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Slug</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Creado</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredProspects.map((prospect) => (
              <tr key={prospect.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{prospect.nombre}</td>
                <td className="px-4 py-3 text-gray-600">{prospect.ciudad}</td>
                <td className="px-4 py-3 text-gray-600">{prospect.telefono}</td>
                <td className="px-4 py-3">
                  {prospect.whatsapp ? (
                    <a
                      href={`https://wa.me/${prospect.whatsapp}`}
                      target="_blank"
rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-green-600 hover:text-green-700"
                    >
                      <MessageSquare className="w-4 h-4" />
                      {prospect.whatsapp}
                    </a>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${ESTADO_COLORS[prospect.estado]}`}>
                    {prospect.estado}
                  </span>
                </td>
                <td className="px-4 py-3 text-blue-600 text-sm">
                  demo.yaweb.ai/{prospect.slug}
                </td>
                <td className="px-4 py-3 text-gray-600 text-sm">
                  {new Date(prospect.created_at).toLocaleDateString('es-ES')}
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button className="p-1 text-gray-600 hover:text-blue-600" title="Ver">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="p-1 text-gray-600 hover:text-green-600" title="Generar Demo">
                      <FileText className="w-4 h-4" />
                    </button>
                    <button className="p-1 text-gray-600 hover:text-green-600" title="WhatsApp">
                      <MessageSquare className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {loading && (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          </div>
        )}
        {!loading && filteredProspects.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No hay prospectos en esta categoria.
          </div>
        )}
      </div>
    </div>
  );
};

const WhatsAppSection = ({ selectedProspects }: { selectedProspects: Prospect[] }) => {
  const [template, setTemplate] = useState(WHATSAPP_TEMPLATES[0]);
  const [preview, setPreview] = useState('');
  const [sending, setSending] = useState(false);
  const [sentCount, setSentCount] = useState(0);
  const [rateLimit, setRateLimit] = useState({ current: 0, max: 100 });

  useEffect(() => {
    const filled = template.template
      .replace('{nombre}', selectedProspects[0]?.nombre || 'Nombre')
      .replace('{negocio}', selectedProspects[0]?.nombre || 'Negocio')
      .replace('{ciudad}', selectedProspects[0]?.ciudad || 'Ciudad')
      .replace('{demo_url}', selectedProspects[0] ? `demo.yaweb.ai/${selectedProspects[0].slug}` : 'demo.yaweb.ai/slug');
    setPreview(filled);
  }, [template, selectedProspects]);

  const handleSend = async () => {
    setSending(true);
    try {
      await fetch(`${API_BASE_URL}/api/whatsapp/send-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prospect_ids: selectedProspects.map((p) => p.id),
          template_id: template.id,
        }),
      });
      setSentCount(selectedProspects.length);
      setRateLimit((prev) => ({ ...prev, current: prev.current + selectedProspects.length }));
    } catch (error) {
      console.error('Send batch error:', error);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
      <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <MessageSquare className="w-5 h-5" />
        Enviar WhatsApp
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Plantilla</label>
          <div className="relative">
            <select
              value={template.id}
              onChange={(e) => setTemplate(WHATSAPP_TEMPLATES.find((t) => t.id === e.target.value) || WHATSAPP_TEMPLATES[0])}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none"
            >
              {WHATSAPP_TEMPLATES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
            <ChevronDown className="w-5 h-5 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Vista Previa</label>
            <textarea
              value={preview}
              onChange={(e) => setPreview(e.target.value)}
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
            />
          </div>

          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Prospectos seleccionados:</span>
              <span className="font-semibold">{selectedProspects.length}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Limite de tasa:</span>
              <span className="text-sm">
                {rateLimit.current} / {rateLimit.max}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${(rateLimit.current / rateLimit.max) * 100}%` }}
              />
            </div>
          </div>

          <button
            onClick={handleSend}
            disabled={sending || selectedProspects.length === 0}
            className="w-full mt-4 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {sending ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            {sending ? 'Enviando...' : 'Enviar Mensajes'}
          </button>

          {sentCount > 0 && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700">
              <CheckCircle className="w-5 h-5" />
              {sentCount} mensajes enviados exitosamente!
            </div>
          )}
        </div>

        <div className="border-l pl-6">
          <h3 className="font-medium text-gray-700 mb-4">Prospectos Seleccionados</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {selectedProspects.length === 0 ? (
              <p className="text-gray-500 text-sm">Selecciona prospectos de la tabla de arriba.</p>
            ) : (
              selectedProspects.map((prospect) => (
                <div key={prospect.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{prospect.nombre}</p>
                    <p className="text-sm text-gray-500">{prospect.ciudad}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {prospect.whatsapp ? (
                      <span className="w-2 h-2 rounded-full bg-green-500" title="WhatsApp disponible" />
                    ) : (
                      <span className="w-2 h-2 rounded-full bg-gray-400" title="Sin WhatsApp" />
                    )}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${ESTADO_COLORS[prospect.estado]}`}>
                      {prospect.estado}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const GeneratedWebs = ({ onActivate }: { onActivate: (web: GeneratedWeb) => void }) => {
  const [webs, setWebs] = useState<GeneratedWeb[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchWebs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/webs`);
      const data = await response.json();
      setWebs(data);
    } catch (error) {
      console.error('Fetch webs error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWebs();
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Globe className="w-5 h-5" />
          Webs Creadas
        </h2>
        <button
          onClick={fetchWebs}
          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded-lg"
          title="Actualizar"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">ID</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nombre</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Plan</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Creado</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Preview URL</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Estado</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {webs.map((web) => (
              <tr key={web.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-sm">{web.id.slice(0, 8)}</td>
                <td className="px-4 py-3 font-medium">{web.nombre}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                    {web.plan}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600 text-sm">
                  {new Date(web.created_at).toLocaleDateString('es-ES')}
                </td>
                <td className="px-4 py-3">
                  <a
                    href={web.preview_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700 flex items-center gap-1 text-sm"
                  >
                    {web.slug}.yaweb.ai
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    web.estado === 'active'
                      ? 'bg-green-100 text-green-800'
                      : web.estado === 'pending'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {web.estado}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <a
                      href={web.preview_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 text-gray-600 hover:text-blue-600"
                      title="Ver Preview"
                    >
                      <Eye className="w-4 h-4" />
                    </a>
                    <button
                      onClick={() => onActivate(web)}
                      className="p-1 text-gray-600 hover:text-green-600"
                      title="Activar"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button className="p-1 text-gray-600 hover:text-blue-600" title="Descargar">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {loading && (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          </div>
        )}
        {!loading && webs.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No hay webs generadas todavia.
          </div>
        )}
      </div>
    </div>
  );
};

const ActivationModal = ({
  isOpen,
  onClose,
  item,
}: {
  isOpen: boolean;
  onClose: () => void;
  item: Prospect | GeneratedWeb | null;
}) => {
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [activated, setActivated] = useState(false);

  const handleActivate = async () => {
    setProcessing(true);
    // Simulate Stripe payment
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setProcessing(false);
    setSuccess(true);
    setActivated(true);
  };

  if (!isOpen || !item) return null;

  const slug = 'slug' in item ? item.slug : '';
  const nombre = 'nombre' in item ? item.nombre : '';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 overflow-hidden">
        {!success ? (
          <>
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Activar Web</h3>
                <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Globe className="w-8 h-8 text-blue-600" />
                </div>
                <h4 className="font-medium text-lg">{nombre}</h4>
                <p className="text-gray-500">demo.yaweb.ai/{slug}</p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h5 className="font-medium mb-3">Plan de Precios</h5>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Primer ano</span>
                    <span className="font-semibold">99€</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Anos siguientes</span>
                    <span className="font-semibold">49€/ano</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleActivate}
disabled={processing}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {processing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Procesando pago...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Pagar y Activar (99€)
                  </>
                )}
              </button>
            </div>
          </>
        ) : (
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h4 className="font-medium text-lg mb-2">Activada!</h4>
            <p className="text-gray-500 mb-4">Tu web esta lista y activa.</p>
            <a
              href={`https://${slug}.yaweb.ai`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 mb-4"
            >
              Ver {slug}.yaweb.ai
              <ExternalLink className="w-4 h-4" />
            </a>
            <button
              onClick={onClose}
              className="block w-full text-gray-600 hover:text-gray-800"
            >
              Cerrar
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Web Creator Component
const WebCreatorSection = () => {
  const [config, setConfig] = useState<WebCreatorConfig>({
    google_business_url: '',
    contexto_adicional: '',
    email: '',
    telefono: '',
    whatsapp: '',
    modelo_ia: 'gpt-4o-mini',
    tema: 'claro',
    estilo: 'moderno',
    tono: 'cercano',
    densidad: 'completo',
    color_primario: '#3B82F6',
  });
  const [currentStep, setCurrentStep] = useState(1);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [generationComplete, setGenerationComplete] = useState(false);
  const [generatedSlug, setGeneratedSlug] = useState('');
  const [history, setHistory] = useState<GenerationHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [scrapingGoogle, setScrapingGoogle] = useState(false);
  const [googleData, setGoogleData] = useState<any>(null);
  const [showPreview, setShowPreview] = useState(false);
  
  // Color presets
  const colorPresets = [
    { name: 'Azul', color: '#3B82F6' },
    { name: 'Rojo', color: '#EF4444' },
    { name: 'Verde', color: '#22C55E' },
    { name: 'Amarillo', color: '#EAB308' },
    { name: 'Morado', color: '#8B5CF6' },
    { name: 'Rosa', color: '#EC4899' },
    { name: 'Naranja', color: '#F97316' },
    { name: 'Gris', color: '#6B7280' },
  ];

  // Fetch history
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generator/history`);
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      // Use mock data
      setHistory([
        { id: '1', nombre: 'Restaurante El Parque', slug: 'restaurante-el-parque', created_at: new Date().toISOString(), preview_url: '#', config: {} },
        { id: '2', nombre: 'Peluqueria María', slug: 'peluqueria-maria', created_at: new Date(Date.now() - 86400000).toISOString(), preview_url: '#', config: {} },
      ]);
    }
  };

  const handleScrapeGoogle = async () => {
    if (!config.google_business_url) return;
    setScrapingGoogle(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/scraper/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: config.google_business_url }),
      });
      const data = await response.json();
      setGoogleData(data);
      // Auto-fill form with scraped data
      if (data.email) setConfig(prev => ({ ...prev, email: data.email }));
      if (data.phone) setConfig(prev => ({ ...prev, telefono: data.phone }));
      if (data.whatsapp) setConfig(prev => ({ ...prev, whatsapp: data.whatsapp }));
    } catch (error) {
      console.error('Google scrape error:', error);
    } finally {
      setScrapingGoogle(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setProgress(0);
    
    // Simulate generation progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 15;
      });
    }, 500);

    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      const data = await response.json();
      clearInterval(progressInterval);
      setProgress(100);
      setGeneratedSlug(data.slug || 'web-generada');
      setGenerationComplete(true);
      fetchHistory();
    } catch (error) {
      clearInterval(progressInterval);
      // Demo mode - simulate success
      setTimeout(() => {
        setProgress(100);
        const slug = config.google_business_url.split('/').pop()?.replace(/[^a-zA-Z0-9]/g, '-') || 'web-demo';
        setGeneratedSlug(slug);
        setGenerationComplete(true);
        fetchHistory();
      }, 3000);
    } finally {
      setGenerating(false);
    }
  };

  const handleClone = (item: GenerationHistory) => {
    setConfig(prev => ({
      ...prev,
      google_business_url: item.config.google_business_url || '',
      contexto_adicional: item.config.contexto_adicional || '',
      email: item.config.email || '',
      telefono: item.config.telefono || '',
      whatsapp: item.config.whatsapp || '',
      modelo_ia: item.config.modelo_ia || 'gpt-4o-mini',
      tema: item.config.tema || 'claro',
      estilo: item.config.estilo || 'moderno',
      tono: item.config.tono || 'cercano',
      densidad: item.config.densidad || 'completo',
    }));
    setShowHistory(false);
  };

  const resetForm = () => {
    setConfig({
      google_business_url: '',
      contexto_adicional: '',
      email: '',
      telefono: '',
      whatsapp: '',
      modelo_ia: 'gpt-4o-mini',
      tema: 'claro',
      estilo: 'moderno',
      tono: 'cercano',
      densidad: 'completo',
      color_primario: '#3B82F6',
    });
    setCurrentStep(1);
    setGenerationComplete(false);
    setGeneratedSlug('');
    setGoogleData(null);
  };

  const selectedModel = AI_MODELS_FOR_WEB.find(m => m.id === config.modelo_ia);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`rounded-xl shadow-sm p-6 bg-gradient-to-r ${TEMA_COLORS[config.tema].accent} text-white`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Wand2 className="w-8 h-8" />
            <div>
              <h2 className="text-xl font-semibold">Creador de Webs</h2>
              <p className="text-white/80 text-sm">Genera webs profesionales para negocios locales</p>
            </div>
          </div>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg flex items-center gap-2 transition-colors"
          >
            <History className="w-4 h-4" />
            Historial
          </button>
        </div>
      </div>

      {/* Step Progress */}
      {!generationComplete && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            {WEB_BUILDER_STEPS.map((step) => (
              <div key={step.step} className="flex items-center">
                <button
                  onClick={() => setCurrentStep(step.step)}
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                    currentStep === step.step
                      ? 'bg-blue-600 text-white scale-110'
                      : currentStep > step.step
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {currentStep > step.step ? <Check className="w-5 h-5" /> : step.step}
                </button>
                {step.step < 5 && (
                  <div className={`w-16 h-1 mx-2 rounded ${
                    currentStep > step.step ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between text-sm">
            {WEB_BUILDER_STEPS.map((step) => (
              <span
                key={step.step}
                className={`${
                  currentStep === step.step ? 'text-blue-600 font-medium' : 'text-gray-500'
                }`}
              >
                {step.title}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Generation Complete */}
      {generationComplete && (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold mb-2">¡Web Generada!</h3>
          <p className="text-gray-500 mb-6">Tu web está lista para visualizar y descargar</p>
          <div className="flex items-center justify-center gap-4 mb-6">
            <a
              href={`https://${generatedSlug}.yaweb.ai`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Eye className="w-5 h-5" />
              Ver Web
              <ExternalLink className="w-4 h-4" />
            </a>
            <button className="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 flex items-center gap-2">
              <Download className="w-5 h-5" />
              Descargar ZIP
            </button>
          </div>
          <button
            onClick={resetForm}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            + Crear otra web
          </button>
        </div>
      )}

      {/* History Modal */}
      {showHistory && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <History className="w-5 h-5" />
              Historial de Generaciones
            </h3>
            <button onClick={() => setShowHistory(false)} className="p-1 hover:bg-gray-100 rounded">
              <X className="w-5 h-5" />
            </button>
          </div>
          {history.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No hay generaciones anteriores</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {history.map((item) => (
                <div key={item.id} className="border rounded-lg p-4 hover:border-blue-300 transition-colors">
                  <h4 className="font-medium mb-2">{item.nombre}</h4>
                  <p className="text-sm text-gray-500 mb-2">demo.yaweb.ai/{item.slug}</p>
                  <p className="text-xs text-gray-400 mb-3">
                    {new Date(item.created_at).toLocaleDateString('es-ES')}
                  </p>
                  <div className="flex gap-2">
                    <button className="p-2 text-gray-600 hover:text-blue-600" title="Ver">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleClone(item)}
                      className="p-2 text-gray-600 hover:text-blue-600"
                      title="Clonar"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Main Form */}
      {!generationComplete && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Step 1: Google Business URL */}
            <div className={`bg-white rounded-xl shadow-sm p-6 ${currentStep !== 1 ? 'opacity-50' : ''}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="font-bold text-blue-600">1</span>
                </div>
                <div>
                  <h3 className="font-semibold">URL Google Business</h3>
                  <p className="text-sm text-gray-500">{WEB_BUILDER_STEPS[0].description}</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Link className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="url"
                    value={config.google_business_url}
                    onChange={(e) => setConfig(prev => ({ ...prev, google_business_url: e.target.value }))}
                    placeholder="https://business.google.com/..."
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button
                  onClick={handleScrapeGoogle}
                  disabled={!config.google_business_url || scrapingGoogle}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
                >
                  {scrapingGoogle ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  {scrapingGoogle ? 'Extrayendo...' : 'Extraer Datos'}
                </button>
              </div>
              {googleData && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-700 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    Datos extraídos correctamente
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Nombre: <strong>{googleData.nombre || 'No disponible'}</strong>
                  </p>
                </div>
              )}
            </div>

            {/* Step 2: Contact Info */}
            <div className={`bg-white rounded-xl shadow-sm p-6 ${currentStep !== 2 ? 'opacity-50' : ''}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="font-bold text-purple-600">2</span>
                </div>
                <div>
                  <h3 className="font-semibold">Datos de Contacto</h3>
                  <p className="text-sm text-gray-500">{WEB_BUILDER_STEPS[1].description}</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={config.email}
                    onChange={(e) => setConfig(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="contacto@negocio.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                  <input
                    type="tel"
                    value={config.telefono}
                    onChange={(e) => setConfig(prev => ({ ...prev, telefono: e.target.value }))}
                    placeholder="+34 912 345 678"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">WhatsApp</label>
                  <input
                    type="tel"
                    value={config.whatsapp}
                    onChange={(e) => setConfig(prev => ({ ...prev, whatsapp: e.target.value }))}
                    placeholder="+34 600 123 456"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Step 3: AI Model */}
            <div className={`bg-white rounded-xl shadow-sm p-6 ${currentStep !== 3 ? 'opacity-50' : ''}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="font-bold text-green-600">3</span>
                </div>
                <div>
                  <h3 className="font-semibold">Configuración de IA</h3>
                  <p className="text-sm text-gray-500">{WEB_BUILDER_STEPS[2].description}</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Modelo de IA</label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {AI_MODELS_FOR_WEB.map((model) => (
                      <button
                        key={model.id}
                        onClick={() => setConfig(prev => ({ ...prev, modelo_ia: model.id }))}
                        className={`p-4 rounded-lg border-2 text-left transition-all ${
                          config.modelo_ia === model.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold">{model.name}</span>
                          <span className={`text-sm ${model.cost === '0€' ? 'text-green-600' : 'text-gray-500'}`}>
                            {model.cost}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500">{model.description}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Step 4: Style */}
            <div className={`bg-white rounded-xl shadow-sm p-6 ${currentStep !== 4 ? 'opacity-50' : ''}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                  <span className="font-bold text-orange-600">4</span>
                </div>
                <div>
                  <h3 className="font-semibold">Estilo y Diseño</h3>
                  <p className="text-sm text-gray-500">{WEB_BUILDER_STEPS[3].description}</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Theme Toggle */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Tema</label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, tema: 'claro' }))}
                      className={`flex-1 p-3 rounded-lg border-2 flex items-center gap-2 transition-all ${
                        config.tema === 'claro' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <Sun className="w-5 h-5" />
                      <span>Claro</span>
                    </button>
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, tema: 'oscuro' }))}
                      className={`flex-1 p-3 rounded-lg border-2 flex items-center gap-2 transition-all ${
                        config.tema === 'oscuro' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <Moon className="w-5 h-5" />
                      <span>Oscuro</span>
                    </button>
                  </div>
                </div>

                {/* Style */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Estilo</label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, estilo: 'moderno' }))}
                      className={`flex-1 p-3 rounded-lg border-2 text-center transition-all ${
                        config.estilo === 'moderno' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <Zap className="w-5 h-5 mx-auto mb-1" />
                      <span className="text-sm">Moderno</span>
                    </button>
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, estilo: 'clasico' }))}
                      className={`flex-1 p-3 rounded-lg border-2 text-center transition-all ${
                        config.estilo === 'clasico' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <Building2 className="w-5 h-5 mx-auto mb-1" />
                      <span className="text-sm">Clásico</span>
                    </button>
                  </div>
                </div>

                {/* Tone */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Tono</label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, tono: 'cercano' }))}
                      className={`flex-1 p-3 rounded-lg border-2 text-center transition-all ${
                        config.tono === 'cercano' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <Users className="w-5 h-5 mx-auto mb-1" />
                      <span className="text-sm">Cercano</span>
                    </button>
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, tono: 'formal' }))}
                      className={`flex-1 p-3 rounded-lg border-2 text-center transition-all ${
                        config.tono === 'formal' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <Settings className="w-5 h-5 mx-auto mb-1" />
                      <span className="text-sm">Formal</span>
                    </button>
                  </div>
                </div>

                {/* Density */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Densidad</label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, densidad: 'completo' }))}
                      className={`flex-1 p-3 rounded-lg border-2 flex items-center gap-2 transition-all ${
                        config.densidad === 'completo' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <AlignJustify className="w-5 h-5" />
                      <span>Completo</span>
                    </button>
                    <button
                      onClick={() => setConfig(prev => ({ ...prev, densidad: 'minimo' }))}
                      className={`flex-1 p-3 rounded-lg border-2 flex items-center gap-2 transition-all ${
                        config.densidad === 'minimo' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                      }`}
                    >
                      <Type className="w-5 h-5" />
                      <span>Mínimo</span>
                    </button>
                  </div>
                </div>

                {/* Color Picker */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Palette className="w-4 h-4 inline mr-1" />
                    Color Principal
                  </label>
                  <div className="flex items-center gap-4">
                    <div className="flex gap-2">
                      {colorPresets.map((preset) => (
                        <button
                          key={preset.color}
                          onClick={() => setConfig(prev => ({ ...prev, color_primario: preset.color }))}
                          className={`w-8 h-8 rounded-full border-2 transition-all ${
                            config.color_primario === preset.color ? 'border-gray-900 scale-110' : 'border-transparent'
                          }`}
                          style={{backgroundColor: preset.color }}
                          title={preset.name}
                        />
                      ))}
                    </div>
                    <input
                      type="color"
                      value={config.color_primario}
                      onChange={(e) => setConfig(prev => ({ ...prev, color_primario: e.target.value }))}
                      className="w-12 h-8 rounded cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              {/* Contexto adicional */}
              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contexto Adicional
                </label>
                <textarea
                  value={config.contexto_adicional}
                  onChange={(e) => setConfig(prev => ({ ...prev, contexto_adicional: e.target.value }))}
                  rows={4}
                  placeholder="Información adicional sobre el negocio, servicios especiales, historia, etc."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Step 5: Generate */}
            <div className={`bg-white rounded-xl shadow-sm p-6 ${currentStep !== 5 ? 'opacity-50' : ''}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-pink-100 rounded-full flex items-center justify-center">
                  <span className="font-bold text-pink-600">5</span>
                </div>
                <div>
                  <h3 className="font-semibold">Generar Web</h3>
                  <p className="text-sm text-gray-500">{WEB_BUILDER_STEPS[4].description}</p>
                </div>
              </div>

              {/* Preview Summary */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="font-medium mb-3">Resumen de Configuración</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Modelo:</span>
                    <p className="font-medium">{selectedModel?.name}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Coste:</span>
                    <p className={`font-medium ${selectedModel?.cost === '0€' ? 'text-green-600' : 'text-gray-900'}`}>
                      {selectedModel?.cost}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Tema:</span>
                    <p className="font-medium capitalize">{config.tema}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Estilo:</span>
                    <p className="font-medium capitalize">{config.estilo}</p>
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: config.color_primario }} />
                  <span className="text-sm">Color: {config.color_primario}</span>
                </div>
              </div>

              {/* Generate Button */}
              {!generating ? (
                <button
                  onClick={handleGenerate}
                  disabled={!config.email || !config.telefono}
                  className="w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-3 text-lg font-semibold"
                >
                  <Wand2 className="w-6 h-6" />
                  Generar Web
                </button>
              ) : (
                <div className="space-y-3">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Generando contenido con {selectedModel?.name}...</span>
                      <span className="text-sm">{Math.round(progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 text-center">
                    Esto puede tardar entre 10-30 segundos dependiendo del modelo...
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Live Preview */}
          <div className="lg:col-span-1">
            <div className={`sticky top-4 rounded-xl shadow-lg overflow-hidden ${
              config.tema === 'oscuro' ? 'bg-gray-900' : 'bg-white'
            }`}>
              <div className="p-4 border-b flex items-center justify-between">
                <span className="text-sm font-medium">Vista Previa</span>
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {showPreview ? 'Ocultar' : 'Mostrar'}
                </button>
              </div>
              
              {/* Mini Preview */}
              <div className={`p-4 ${showPreview ? '' : 'blur-sm'}`}>
                <div className="w-full h-40 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg mb-4 flex items-center justify-center">
                  <Globe className={`w-16 h-16 ${config.tema === 'oscuro' ? 'text-gray-600' : 'text-blue-400'}`} />
                </div>
                <h4 className={`font-semibold mb-2 ${config.tema === 'oscuro' ? 'text-white' : ''}`}>
                  {googleData?.nombre || 'Nombre del Negocio'}
                </h4>
                <p className={`text-sm mb-4 ${config.tema === 'oscuro' ? 'text-gray-400' : 'text-gray-600'}`}>
                  {config.contexto_adicional || 'Descripción breve del negocio...'}
                </p>
                <div className={`text-sm ${config.tema === 'oscuro' ? 'text-gray-400' : 'text-gray-500'}`}>
                  <p>{config.email}</p>
                  <p>{config.telefono}</p>
                </div>
                <div className="flex gap-2 mt-4">
                  {config.estilo === 'moderno' ? (
                    <div className="w-full h-8 bg-gray-200 rounded-lg" />
                  ) : (
                    <div className="w-full h-8 bg-gray-200 rounded border-2 border-gray-400" />
                  )}
                </div>
              </div>

              {/* Color Preview */}
              <div className="p-4 border-t">
                <p className="text-xs text-gray-500 mb-2">Paleta de colores</p>
                <div className="flex gap-1">
                  <div className="w-1/4 h-8 rounded-l" style={{ backgroundColor: config.color_primario }} />
                  <div className="w-1/4 h-8" style={{ backgroundColor: config.color_primario + '80' }} />
                  <div className="w-1/4 h-8" style={{ backgroundColor: config.color_primario + '40' }} />
                  <div className={`w-1/4 h-8 rounded-r ${config.tema === 'oscuro' ? 'bg-gray-800' : 'bg-gray-100'}`} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// AI Settings Component
const AISettingsSection = () => {
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2000);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/ai/providers`);
      const data = await response.json();
      setProviders(data);
      
      // Fetch current config
      const configRes = await fetch(`${API_BASE_URL}/api/settings/ai`);
      const config: AIConfig = await configRes.json();
      setSelectedProvider(config.provider);
      setSelectedModel(config.model);
      setTemperature(config.temperature);
      setMaxTokens(config.max_tokens);
    } catch (error) {
      console.error('Failed to fetch AI settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/ai`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          model: selectedModel,
          api_key: apiKey || undefined,
          temperature,
          max_tokens: maxTokens,
        }),
      });
      const data = await response.json();
      setMessage({ type: 'success', text: 'Configuración guardada correctamente' });
      setApiKey('');
      // Refresh providers to update has_api_key status
      fetchProviders();
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al guardar la configuración' });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/settings/ai/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          model: selectedModel,
          api_key: apiKey || undefined,
        }),
      });
      const data = await response.json();
      setTestResult({
        success: data.success,
        message: data.success ? `✓ Conexión exitosa: ${data.generated_title}` : `✗ Error: ${data.error}`,
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Error al probar la conexión',
      });
    } finally {
      setTesting(false);
    }
  };

  const currentProvider = providers.find(p => p.id === selectedProvider);
  const currentModels = currentProvider?.models || [];

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-sm p-6 text-white">
        <div className="flex items-center gap-3">
          <Sparkles className="w-8 h-8" />
          <div>
            <h2 className="text-xl font-semibold">Configuración de IA</h2>
            <p className="text-purple-100 text-sm">Selecciona el proveedor y modelo para generación de contenido</p>
          </div>
        </div>
      </div>

      {/* Provider Selection */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Bot className="w-5 h-5" />
          Proveedor de IA
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {providers.map((provider) => (
            <button
              key={provider.id}
              onClick={() => {
                setSelectedProvider(provider.id);
                setSelectedModel(provider.models[0]?.id || '');
              }}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                selectedProvider === provider.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold">{provider.name}</span>
                {provider.has_api_key ? (
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Configurado</span>
                ) : provider.id === 'mock' ? (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">Gratis</span>
                ) : (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">Sin clave</span>
                )}
              </div>
              <p className="text-sm text-gray-500">
                {provider.models.length} modelo{provider.models.length !== 1 ? 's' : ''} disponible{provider.models.length !== 1 ? 's' : ''}
              </p>
            </button>
          ))}
        </div>

        {/* Model Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Modelo</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {currentModels.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name} - {model.description}
              </option>
            ))}
          </select>
        </div>

        {/* API Key */}
        {selectedProvider !== 'mock' && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Key className="w-4 h-4 inline mr-1" />
              API Key {currentProvider?.has_api_key && <span className="text-green-600 text-xs">(Guardada)</span>}
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={currentProvider?.has_api_key ? 'Nueva clave (dejar vacío para mantener)' : 'Introduce tu API key'}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              {selectedProvider === 'openai' && 'Obtén tu clave en: platform.openai.com/api-keys'}
              {selectedProvider === 'anthropic' && 'Obtén tu clave en: console.anthropic.com/settings/keys'}
              {selectedProvider === 'google' && 'Obtén tu clave en: aistudio.google.com/apikey'}
              {selectedProvider === 'minimax' && 'Obtén tu clave en: platform.minimaxi.com'}
            </p>
          </div>
        )}

        {/* Advanced Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temperatura: {temperature}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">Más bajo = más predecible, más alto = más creativo</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Tokens: {maxTokens}
            </label>
            <input
              type="range"
              min="500"
              max="4000"
              step="500"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">Longitud máxima de la respuesta</p>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
            {message.text}
          </div>
        )}

        {/* Test Result */}
        {testResult && (
          <div className={`mb-6 p-4 rounded-lg ${
            testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}>
            {testResult.message}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={handleTest}
            disabled={testing || selectedProvider === 'mock'}
            className="px-6 py-2 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {testing ? <Loader2 className="w-5 h-5 animate-spin" /> : <TestTube className="w-5 h-5" />}
            Probar Conexión
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
            Guardar Configuración
          </button>
        </div>
      </div>

      {/* Model Comparison */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Comparativa de Modelos</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Proveedor</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Modelo</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Mejor Para</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Coste/Web</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Coste Total</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Calidad</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {currentModels.map((model) => (
                <tr key={model.id} className={`hover:bg-gray-50 ${selectedModel === model.id ? 'bg-blue-50' : ''}`}>
                  <td className="px-4 py-3"><span className="font-medium">{currentProvider?.name}</span></td>
                  <td className="px-4 py-3">{model.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{model.description}</td>
                  <td className="px-4 py-3">
                    <span className={`font-semibold ${model.cost_per_generation_usd === 0 ? 'text-green-600' : 'text-orange-600'}`}>
                      {model.cost_per_generation_usd === 0 ? 'Gratis' : `$${model.cost_per_generation_usd.toFixed(4)}`}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    ${model.input_cost_per_1m_tokens.toFixed(2)} / ${model.output_cost_per_1m_tokens.toFixed(2)} per 1M
                  </td>
                  <td className="px-4 py-3">
                    {model.id.includes('4o') || model.id.includes('sonnet') ? (
                      <span className="text-green-600">★★★★★</span>
                    ) : model.id.includes('haiku') || model.id.includes('flash') ? (
                      <span className="text-yellow-600">★★★</span>
                    ) : (
                      <span className="text-green-600">★★★★</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Cost Calculator */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium mb-3">Calculadora de Costos Estimados</h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm text-gray-600">Webs/mes</label>
              <select className="w-full mt-1 px-3 py-2 border rounded-lg">
                <option value="10">10 webs</option>
                <option value="50">50 webs</option>
                <option value="100">100 webs</option>
                <option value="500">500 webs</option>
              </select>
            </div>
            {currentModels.slice(0, 3).map((model) => (
              <div key={model.id} className="text-center p-3 bg-white rounded-lg border">
                <p className="text-sm text-gray-600">{model.name}</p>
                <p className={`text-xl font-bold ${model.cost_per_generation_usd === 0 ? 'text-green-600' : 'text-blue-600'}`}>
                  {model.cost_per_generation_usd === 0 ? 'Gratis' : `$${(model.cost_per_generation_usd * 100).toFixed(2)}/mes`}
                </p>
              </div>
            ))}
          </div>
        </div>
        
        <p className="text-sm text-gray-500 mt-4">
          <strong>Recomendación:</strong> Para mejores resultados profesionales, usa <strong>Claude 3.5 Sonnet</strong> (mejor relación calidad/precio ~$0.036/web) o <strong>GPT-4o</strong> (mejor calidad general ~$0.025/web). Gemini Flash es el más económico (~$0.00075/web).
        </p>
      </div>
    </div>
  );
};

// Main Component
export default function Dashboard() {
  const [activeSection, setActiveSection] = useState('stats');
  const [stats, setStats] = useState<Stats>({
    total_scans: 0,
    prospects_found: 0,
    demos_generated: 0,
    whatsapp_sent: 0,
  });
  const [activationItem, setActivationItem] = useState<Prospect | GeneratedWeb | null>(null);
  const [showActivationModal, setShowActivationModal] = useState(false);
  const [activationSuccess, setActivationSuccess] = useState(false);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      // Use mock data for demo
      setStats({
        total_scans: 1247,
        prospects_found: 438,
        demos_generated: 156,
        whatsapp_sent: 89,
      });
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleActivate = (item: Prospect | GeneratedWeb) => {
    setActivationItem(item);
    setShowActivationModal(true);
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />

      <main className="flex-1 ml-64 p-8">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {activeSection === 'stats' && 'Dashboard'}
              {activeSection === 'scraper' && 'Scraper de Negocios'}
              {activeSection === 'creator' && 'Creador de Webs'}
              {activeSection === 'prospects' && 'Prospectos'}
              {activeSection === 'whatsapp' && 'WhatsApp'}
              {activeSection === 'webs' && 'Webs Creadas'}
              {activeSection === 'ai-settings' && 'Configuración de IA'}
            </h1>
            <p className="text-gray-500">Panel de administracion de YAWEB.AI</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              Ultima actualizacion: {new Date().toLocaleTimeString('es-ES')}
            </span>
            <button
              onClick={fetchStats}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-white rounded-lg"
              title="Actualizar"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </header>

        {(activeSection === 'stats' || activeSection === 'creator') && (
          <>
            {activeSection === 'creator' && <WebCreatorSection />}
            {activeSection === 'stats' && (
              <>
                <ScraperSection onProspectCreated={fetchStats} />
                <WebCreatorSection />
              </>
            )}
          </>
        )}

        {(activeSection === 'stats' || activeSection === 'prospects') && (
          <ProspectsTable />
        )}

        {(activeSection === 'stats' || activeSection === 'whatsapp') && (
          <WhatsAppSection selectedProspects={[]} />
        )}

        {(activeSection === 'stats' || activeSection === 'webs') && (
          <GeneratedWebs onActivate={handleActivate} />
        )}

        {activeSection === 'ai-settings' && (
          <AISettingsSection />
        )}

        {activeSection === 'stats' && (
          <>
            <ProspectsTable />
            <WhatsAppSection selectedProspects={[]} />
            <GeneratedWebs onActivate={handleActivate} />
          </>
        )}
      </main>

      <ActivationModal
        isOpen={showActivationModal}
        onClose={() => {
          setShowActivationModal(false);
          setActivationItem(null);
          setActivationSuccess(false);
        }}
        item={activationItem}
      />
    </div>
  );
}
