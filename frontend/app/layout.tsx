import React from 'react'
// @ts-ignore
import './globals.css'

export const metadata = {
  title: 'AutoDevOS - Build websites with AI',
  description: 'Autonomous AI agents build and refine your company website',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">{children}</body>
    </html>
  )
}
