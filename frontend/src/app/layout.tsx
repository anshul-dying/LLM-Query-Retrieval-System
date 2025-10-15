import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LLM Query Retrieval",
  description: "Upload documents and get concise answers with references.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur bg-[color:var(--surface)] border-b border-[color:var(--border)]">
          <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
            <a href="/" className="font-semibold tracking-tight">LLM Query Retrieval</a>
            <div className="flex items-center gap-2 text-sm">
              <a href="/request" className="rounded-md px-3 py-1.5 hover:bg-[color:var(--accent)]">Request</a>
            </div>
          </div>
        </nav>
        <div className="pt-16 min-h-screen">{children}</div>
      </body>
    </html>
  );
}
