"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sun, Moon } from "lucide-react";

/**
 * Theme toggle button with smooth motion animation.
 * Persists user preference in localStorage and respects system prefers‑color‑scheme.
 */
export default function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Initialise from storage / system preference
  useEffect(() => {
    const saved = typeof window !== 'undefined' && localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setTheme('dark');
      document.documentElement.classList.add('dark');
    } else {
      setTheme('light');
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', newTheme);
  };

  return (
    <motion.button
      onClick={toggleTheme}
      aria-label="Toggle light/dark mode"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="ml-4 flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
    >
      {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </motion.button>
  );
}
