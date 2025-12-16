import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/layout/providers";
import { Toaster } from "@/components/ui/toaster";
import { Header } from "@/components/layout/header";
import { ThemeScript } from "./theme-script";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Invoice LangGraph Agent - AI-Powered Invoice Processing",
  description: "Superhuman invoice processing with RAG-powered answers, real-time workflow tracking, and risk analysis in seconds.",
  other: {
    "color-scheme": "dark",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                // Force dark mode immediately - prevent any theme switching
                document.documentElement.classList.add('dark');
                document.documentElement.classList.remove('light');
                document.documentElement.setAttribute('data-theme', 'dark');
                // Set color-scheme meta tag
                let meta = document.querySelector('meta[name="color-scheme"]');
                if (!meta) {
                  meta = document.createElement('meta');
                  meta.name = 'color-scheme';
                  meta.content = 'dark';
                  document.head.appendChild(meta);
                } else {
                  meta.content = 'dark';
                }
              })();
            `,
          }}
        />
        <ThemeScript />
        <Providers>
          <Header />
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}

