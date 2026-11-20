import { QueryProvider } from '@/components/query-provider';
import { ThemeProvider } from '@/components/theme-provider';
import { APP_TITLE, DEFAULT_THEME, LOGO_SRC } from '@/lib/constants';
import type { Metadata } from 'next';
import type React from 'react';
import './globals.css';

// Sets the dark class before first paint so dark mode never flashes light.
// Keep in sync with components/theme-provider.tsx (localStorage key "theme").
const THEME_SCRIPT = `try{var t=localStorage.getItem("theme")||${JSON.stringify(DEFAULT_THEME)};if(t==="dark"||(t==="system"&&matchMedia("(prefers-color-scheme: dark)").matches))document.documentElement.classList.add("dark")}catch(e){}`;

export const metadata: Metadata = {
  title: APP_TITLE,
  description: 'A governed AI analyst for Snowflake query and warehouse activity',
  icons: { icon: LOGO_SRC },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="min-h-screen antialiased">
        <ThemeProvider>
          <QueryProvider>{children}</QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
