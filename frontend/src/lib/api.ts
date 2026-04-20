// API Client for YAWEB.AI

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface GenerationRequest {
  google_url?: string
  context: string
  plan?: 'basic' | 'premium' | 'lan_plus'
}

export interface GenerationResponse {
  success: boolean
  web_id?: string
  preview_url?: string
  download_url?: string
  generated_at?: string
  error?: string
}

export interface WebListItem {
  id: string
  name: string
  category: string
  plan: string
  created_at: string
  preview_url?: string
  status: string
}

export interface WebDetails {
  id: string
  name: string
  category: string
  plan: string
  google_url?: string
  context: string
  status: string
  created_at: string
  preview_url?: string
  download_url?: string
  content?: GeneratedContent
}

export interface GeneratedContent {
  title: string
  subtitle: string
  about_text: string
  services: string[]
  cta_text: string
  primary_color: string
  opening_hours_html: string
  seo_title: string
  seo_description: string
  social_links: Record<string, string | null>
  menu_pdf_url?: string
  is_restaurant_bar: boolean
}

export async function generateWeb(data: GenerationRequest): Promise<GenerationResponse> {
  const response = await fetch(`${API_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Error al generar la web')
  }

  return response.json()
}

export async function getWebList(): Promise<WebListItem[]> {
  const response = await fetch(`${API_URL}/api/webs`)
  
  if (!response.ok) {
    throw new Error('Error al obtener la lista de webs')
  }

  const data = await response.json()
  return data.webs
}

export async function getWebDetails(webId: string): Promise<WebDetails> {
  const response = await fetch(`${API_URL}/api/webs/${webId}`)
  
  if (!response.ok) {
    throw new Error('Error al obtener los detalles de la web')
  }

  return response.json()
}

export async function deleteWeb(webId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/webs/${webId}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error('Error al eliminar la web')
  }
}

export function getPreviewUrl(webId: string): string {
  return `${API_URL}/preview/${webId}`
}

export function getDownloadUrl(webId: string): string {
  return `${API_URL}/api/webs/${webId}/download`
}
