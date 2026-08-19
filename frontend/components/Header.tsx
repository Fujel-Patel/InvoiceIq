"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import {
  Sparkles,
  History,
  BarChart3,
  Zap,
  Menu,
  X,
  LogOut,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import ThemeToggle from "./ThemeToggle";
import { logout } from "@/lib/api";
import { useAuthStore } from "@/store/useAuthStore";

interface NavItem {
  href: string;
  label: string;
  icon: React.ReactNode;
  ariaLabel: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/history", label: "History", icon: <History className="w-4 h-4" />, ariaLabel: "View extraction history" },
  { href: "/analytics", label: "Analytics", icon: <BarChart3 className="w-4 h-4" />, ariaLabel: "View bill analytics" },
  { href: "/settings", label: "Settings", icon: <Zap className="w-4 h-4" />, ariaLabel: "LLM configuration settings" },
];

export function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout: logoutUser } = useAuthStore();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const navLinkClass = (href: string) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      pathname === href
        ? "bg-primary/10 text-primary"
        : "text-muted-foreground hover:bg-muted hover:text-foreground"
    }`;

  const handleSignOut = async () => {
    try {
      await logout();
      logoutUser();
      router.replace("/login");
    } catch {
      logoutUser();
      router.replace("/login");
    } finally {
      setIsMenuOpen(false);
    }
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        if (buttonRef.current && !buttonRef.current.contains(event.target as Node)) {
          setIsMenuOpen(false);
        }
      }
    };

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isMenuOpen]);

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener("keydown", handleEscape);
    }
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isMenuOpen]);

  return (
    <nav className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between relative">
        {/* Logo - always visible */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl shrink-0">
          <Sparkles className="w-6 h-6 text-primary" />
          InvoiceIQ
        </Link>

        {/* Desktop Navigation - hidden on mobile */}
        <div className="hidden md:flex items-center gap-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-label={item.ariaLabel}
              className={navLinkClass(item.href)}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
          <ThemeToggle />
          <div className="flex items-center gap-2">
            {user && (
              <span className="text-sm text-muted-foreground hidden sm:block">
                {user.email}
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              aria-label="Sign out"
              onClick={handleSignOut}
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>

        {/* Mobile Menu Button - hidden on desktop */}
        <div className="md:hidden flex items-center gap-2">
          <ThemeToggle />
          <button
            ref={buttonRef}
            type="button"
            className="p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-expanded={isMenuOpen}
            aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            aria-controls="mobile-menu"
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Dropdown Menu */}
        {isMenuOpen && (
          <div
            ref={menuRef}
            id="mobile-menu"
            role="menu"
            className="md:hidden absolute right-4 top-full mt-2 w-56 bg-card border border-border/50 rounded-xl shadow-2xl p-2 animate-in fade-in-0 zoom-in-95 duration-150"
          >
            <div className="space-y-1" role="menubar">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-label={item.ariaLabel}
                  role="menuitem"
                  className={cn(
                    navLinkClass(item.href),
                    "w-full justify-start"
                  )}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              ))}
              <hr className="my-2 border-border/50" />
              <div className="flex items-center gap-2 px-3 py-2">
                <ThemeToggle />
              </div>
              {user && (
                <div className="px-3 py-2 text-sm text-muted-foreground">
                  {user.email}
                </div>
              )}
              <hr className="my-2 border-border/50" />
              <button
                role="menuitem"
                onClick={handleSignOut}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  "text-destructive hover:bg-destructive/10 dark:hover:bg-destructive/20"
                )}
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}