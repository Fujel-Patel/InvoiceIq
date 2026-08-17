"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { FileSearch, Shield, Sparkles, Zap, ChevronLeft } from "lucide-react";
import type { ReactNode } from "react";

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  description: string;
  showBack?: boolean;
}

const FEATURES = [
  { icon: FileSearch, text: "AI-powered invoice extraction in seconds" },
  { icon: Shield, text: "Your data stays secure and private" },
  { icon: Zap, text: "Export to CSV or Excel with one click" },
];

function BrandMark({ className }: { className?: string }) {
  return (
    <span
      className={`inline-flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground ${className ?? ""}`}
    >
      <Sparkles className="h-5 w-5" />
    </span>
  );
}

export default function AuthLayout({
  children,
  title,
  description,
  showBack = false,
}: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="grid min-h-screen lg:grid-cols-2">
        {/* Brand panel - hidden on mobile, shown on lg+ */}
        <div className="hidden flex-col justify-between border-r border-border/60 bg-card/40 p-8 lg:p-12 lg:flex">
          <Link href="/" className="inline-flex items-center gap-2 text-xl font-bold">
            <BrandMark />
            InvoiceIQ
          </Link>

          <div className="space-y-6">
            <h2 className="text-2xl lg:text-3xl font-extrabold tracking-tight">
              Invoices, decoded by AI.
            </h2>
            <p className="text-muted-foreground">
              Upload any invoice or receipt and let InvoiceIQ extract vendor,
              amounts, line items, and more in seconds.
            </p>
            <ul className="space-y-3">
              {FEATURES.map((feature) => (
                <li key={feature.text} className="flex items-center gap-3 text-sm">
                  <span className="inline-flex h-8 w-8 items-center justify-center rounded-md border bg-background">
                    <feature.icon className="h-4 w-4 text-primary" />
                  </span>
                  <span className="text-muted-foreground">{feature.text}</span>
                </li>
              ))}
            </ul>
          </div>

          <p className="text-xs text-muted-foreground">InvoiceIQ © 2026</p>
        </div>

        {/* Form panel - full width on mobile, half on lg+ */}
        <div className="flex flex-col items-center justify-center px-4 sm:px-6 py-8 lg:py-12">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="w-full max-w-md"
          >
            <div className="mb-6 inline-flex items-center gap-2 text-xl font-bold lg:hidden">
              <BrandMark />
              InvoiceIQ
            </div>

            {showBack && (
              <div className="mb-6">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Back to login
                </Link>
              </div>
            )}

            <h1 className="text-xl lg:text-2xl font-bold tracking-tight">{title}</h1>
            <p className="mt-1.5 text-sm text-muted-foreground">{description}</p>

            <div className="mt-6 lg:mt-8">{children}</div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
