import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'YAWEB.AI - Tu web profesional en 5 minutos',
  description: 'Genera automáticamente páginas web profesionales para tu negocio local usando IA. Extracción de datos de Google Business Profile incluida.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
