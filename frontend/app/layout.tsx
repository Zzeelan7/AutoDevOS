import React from 'react'
// @ts-ignore - CSS import
import './globals.css'
import { PuterScript } from '@/components/PuterScript'

export const metadata = {
  title: 'AutoDevOS - Build websites with AI',
  description: 'Autonomous AI agents build and refine your company website',
  icons: {
    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">⚡</text></svg>',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="dark">
        {children}
        <PuterScript />
      </body>
    </html>
  )
}
