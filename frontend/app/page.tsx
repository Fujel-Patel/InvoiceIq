"use client";

import { motion } from "framer-motion";
import { Sparkles, FileSearch, Zap, Shield, History } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
/* Theme state handled in ThemeToggle component */
import { Card } from "@/components/ui/card";
import { Toaster } from "sonner";
import Uploader from "@/components/Uploader";
import ThemeToggle from "@/components/ThemeToggle";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function Home() {
  const pathname = usePathname();
  const navLinkClass = (href: string) =>
    `text-sm font-medium flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
      pathname === href ? "text-primary" : "text-muted-foreground hover:text-primary"
    }`;
  // Theme handling
  /* Theme handled by ThemeToggle component */




  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <Toaster position="top-right" richColors />

      {/* Navbar */}
      <nav className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl">
            <Sparkles className="w-6 h-6 text-primary" />
            InvoiceIQ
          </div>
            <Link
              href="/history"
              aria-label="View extraction history"
              className={navLinkClass("/history")}
            >
              <History className="w-4 h-4" />
              History
            </Link>
            <Link
              href="/llm-config"
              aria-label="LLM configuration settings"
              className={`${navLinkClass("/llm-config")} ml-4`}
            >
              <Zap className="w-4 h-4" />
              Settings
            </Link>
            <ThemeToggle />
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-4xl mx-auto px-6 py-16 sm:py-24 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          <Badge variant="secondary" className="gap-1.5 px-3 py-1 text-sm">
            <Sparkles className="w-3.5 h-3.5" />
            AI Powered
          </Badge>
          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight">
            Extract Invoice Data Instantly
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl">
            Upload any invoice or receipt and let AI extract vendor, amounts,
            line items, and more in seconds.
          </p>
        </motion.div>

        {/* Uploader Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-12 w-full max-w-lg"
        >
          <div className="p-1 rounded-xl bg-gradient-to-b from-primary/20 to-primary/5 shadow-2xl">
            <Uploader />
          </div>
        </motion.div>

        {/* Features Row */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-16 flex flex-wrap justify-center gap-4"
        >
          {[
            { icon: Zap, label: "Instant Extraction" },
            { icon: FileSearch, label: "Smart Detection" },
            { icon: Shield, label: "Secure Processing" },
          ].map((feature, i) => (
            <Card
              key={i}
              className="flex items-center gap-2 px-4 py-2 bg-background border shadow-sm"
            >
              <feature.icon className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">{feature.label}</span>
            </Card>
          ))}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center text-sm text-muted-foreground">
        <Separator className="mb-8" />
        InvoiceIQ © 2026
      </footer>
    </div>
  );
}
