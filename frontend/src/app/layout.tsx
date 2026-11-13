import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WARAZ — Issue Clarification & Video Verification",
  description: "Cyber intelligence platform for issue clarification and recycled video tracking",
  icons: {
    icon: "/favicon.png",
  },
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
        <link rel="icon" href="/favicon.png" type="image/png" />
      </head>
      <body className="min-h-full flex flex-col text-slate-100">
        {children}
      </body>
    </html>
  );
}
