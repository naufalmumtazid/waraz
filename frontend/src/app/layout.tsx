import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WARAZ — Issue Clarification & Video Verification",
  description: "Cyber intelligence platform for issue clarification and recycled video tracking",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <head>
        <link rel="stylesheet" href="/tailwind.css" />
      </head>
      <body className="min-h-full flex flex-col text-slate-100">
        {children}
      </body>
    </html>
  );
}
