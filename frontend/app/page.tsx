"use client";

import { motion } from "framer-motion";
import { Sparkles, FileSearch, Zap, Shield, History, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import React from "react";
import { supabase } from "@/lib/supabaseClient";
import { Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Toaster } from "sonner";
import Uploader from "@/components/Uploader";
import ThemeToggle from "@/components/ThemeToggle";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getLLMConfig } from "@/lib/api";

export default function Home() {
  const [checking, setChecking] = React.useState(true);
  const [hasLLMConfig, setHasLLMConfig] = React.useState<boolean | null>(null);
  const router = useRouter();

  React.useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        if (data?.session) {
          setChecking(false);
          return;
        }
      } catch {
        // Supabase unreachable — show app anyway
      }
      // No session — redirect to login
      router.replace('/login');
      setChecking(false);
    };
    checkAuth();
  }, [router]);

  React.useEffect(() => {
    const checkConfig = () => {
      getLLMConfig().then((cfg) => setHasLLMConfig(cfg !== null));
    };
    checkConfig();
    window.addEventListener("focus", checkConfig);
    return () => window.removeEventListener("focus", checkConfig);
  }, []);

  const pathname = usePathname();
  const navLinkClass = (href: string) =>
    `text-sm font-medium flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
      pathname === href ? "text-primary" : "text-muted-foreground hover:text-primary"
    }`;

  if (checking) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

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
              href="/settings"
              aria-label="LLM configuration settings"
              className={navLinkClass("/settings")}
            >
              <Zap className="w-4 h-4" />
              Settings
            </Link>
            <ThemeToggle />
            <Button variant="ghost" size="sm" aria-label="Sign out" onClick={async () => {
              try { await supabase.auth.signOut(); } catch { /* Supabase unreachable */ }
              router.replace('/login');
            }}>
              Sign Out
            </Button>
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

        {/* LLM Config Warning */}
        {hasLLMConfig === false && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 w-full max-w-lg"
          >
            <Card className="border-amber-500/50 bg-amber-500/10 p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium">No LLM provider configured</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Add an API key to start extracting invoice data.
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-amber-500/50 hover:bg-amber-500/10 shrink-0"
                  onClick={() => router.push("/settings")}
                >
                  <Zap className="w-3.5 h-3.5 mr-1.5" />
                  Configure
                </Button>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Uploader Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-12 w-full max-w-lg"
        >
          <div className="p-1 rounded-xl bg-gradient-to-b from-primary/20 to-primary/5 shadow-2xl">
            <Uploader hasLLMConfig={hasLLMConfig ?? true} />
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
