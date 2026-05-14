import type { Metadata } from 'next';
import { ClerkProvider } from '@clerk/nextjs';
import './globals.css';

export const metadata: Metadata = {
  title: 'GENOME — Genetic Health Intelligence',
  description: 'Your personal genetic health analysis platform. Upload your 23andMe data and get AI-powered insights into disease risks, drug interactions, and health protocols.',
  keywords: 'genetic health, 23andMe, genome analysis, DNA, disease risk, pharmacogenomics',
};

import { Providers } from './providers';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        </head>
        <body>
          <AppRouterCacheProvider>
            <Providers>
              {children}
            </Providers>
          </AppRouterCacheProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
