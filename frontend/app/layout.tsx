import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Mental Coach - Your Supportive AI Companion',
  description: 'A supportive mental coach powered by AI to help you on your wellness journey',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

