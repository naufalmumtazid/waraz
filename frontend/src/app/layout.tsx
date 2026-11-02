import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WARAZ — Pelacak Video Daur Ulang",
  description: "Platform Intelijen Analisis Disinformasi & Pelacak Video Daur Ulang",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" className="h-full antialiased dark">
      <head>
        <link rel="stylesheet" href="/tailwind.css" />
      </head>
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100">
        {children}
      </body>
    </html>
  );
}
