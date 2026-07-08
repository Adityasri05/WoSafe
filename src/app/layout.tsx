import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export const metadata: Metadata = {
  title: "WoSafe - AI That Protects Before Danger Begins",
  description: "WoSafe is the world's first AI-powered Women's Safety Intelligence Platform. It predicts, prevents, and responds to danger using artificial intelligence, community tracking, smart navigation, and emergency systems.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased dark`}>
      <body className="min-h-full flex flex-col bg-[#050816] text-white font-sans">
        {children}
      </body>
    </html>
  );
}
