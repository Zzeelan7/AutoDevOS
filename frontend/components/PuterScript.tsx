'use client'

import Script from 'next/script'

export function PuterScript() {
  return (
    <>
      <Script
        src="https://js.puter.com/v2/"
        strategy="beforeInteractive"
        onError={() => {
          console.warn('Puter.js failed to load - running in offline mode');
          if (typeof window !== 'undefined') {
            (window as any).puter = undefined;
          }
        }}
      />
      <Script
        id="puter-init"
        strategy="afterInteractive"
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
    </>
  )
}
