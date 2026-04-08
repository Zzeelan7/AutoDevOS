import React from 'react'
// @ts-ignore - CSS import
import './globals.css'

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
        {/* Puter.js Integration - Free Claude AI Access */}
        <script
          src="https://js.puter.com/v2/"
          onError={() => {
            console.warn('Puter.js failed to load - running in offline mode');
            if (typeof window !== 'undefined') {
              window.puter = undefined;
            }
          }}
          async
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.puterReady = false;
              window.addEventListener('puter-ready', () => {
                window.puterReady = true;
                console.log('✅ Puter.js loaded successfully');
              });
              setTimeout(() => {
                if (!window.puterReady && !window.puter) {
                  console.warn('Puter.js did not load within timeout - offline mode');
                }
              }, 5000);
            `,
          }}
        />
      </head>
      <body className="dark">
        {children}
      </body>
    </html>
  )
}
