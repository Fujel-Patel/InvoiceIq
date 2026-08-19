"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { useRouter, usePathname } from "next/navigation";

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { hydrate, isLoading, isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    let mounted = true;

    const initAuth = async () => {
      await hydrate();

      if (!mounted) return;

      // If we're on login/signup pages and user is authenticated, redirect to home
      const publicPaths = ['/login', '/signup', '/forgot-password', '/reset-password'];
      const isPublicPath = publicPaths.some((path) => pathname.startsWith(path));

      if (isPublicPath && isAuthenticated) {
        router.replace('/');
      }
    };

    initAuth();

    return () => {
      mounted = false;
    };
  }, [hydrate, isAuthenticated, pathname, router]);

  // Show loading state while hydrating
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}