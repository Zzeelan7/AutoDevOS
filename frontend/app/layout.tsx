import React from 'react'
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
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="dark">
        {children}
      </body>
    </html>
  )
}
