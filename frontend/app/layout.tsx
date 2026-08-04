
import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { Toaster } from "sonner";
import AnimatedLayout from "@/components/AnimatedLayout";
import ThemeInitializer from "@/components/ThemeInitializer";

const inter = Inter({subsets:['latin'],variable:'--font-sans'});

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "InvoiceIQ — AI Invoice Extraction & Management",
    template: "%s | InvoiceIQ",
  },
  description:
    "Upload invoices, extract structured data with AI, and manage, track, and export your bills from one place.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn("h-full", "antialiased", geistSans.variable, geistMono.variable, "font-sans", inter.variable)}
    >
      <body className="min-h-full flex flex-col">
        <ThemeInitializer />
        <AnimatedLayout>{children}</AnimatedLayout>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
