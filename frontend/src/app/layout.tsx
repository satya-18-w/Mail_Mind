import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MailMind — AI Email Intelligence",
  description: "AI-powered email classification, priority scoring & smart insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const runtimeConfig = {
    authUrl: process.env.AUTH_URL || process.env.NEXT_PUBLIC_AUTH_URL || "",
    apiUrl: process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "",
  };

  const runtimeConfigScript = `window.__MAILMIND_CONFIG__ = ${JSON.stringify(runtimeConfig)};`;

  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning className={`${inter.variable} font-sans antialiased`}>
        <script dangerouslySetInnerHTML={{ __html: runtimeConfigScript }} />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
