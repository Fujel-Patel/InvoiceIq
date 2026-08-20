"use client";

import { useEffect, useRef } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { useRouter, usePathname } from "next/navigation";

const PUBLIC_PATHS = ["/login", "/signup", "/forgot-password", "/reset-password"];

function isPublicPath(pathname: string) {
  return PUBLIC_PATHS.some((p) => pathname.startsWith(p));
}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { hydrate, isLoading, isAuthenticated } = useAuthStore();
  const initRef = useRef(false);

  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;

    const initAuth = async () => {
      await hydrate();
    };

    initAuth();
  }, [hydrate]);

  // Show loading state while hydrating
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  // Authenticated user on a public page → redirect to home
  if (isPublicPath(pathname) && isAuthenticated) {
    router.replace("/");
    return null;
  }

  // Unauthenticated user on a protected page → redirect to login
  if (!isPublicPath(pathname) && !isAuthenticated) {
    const loginUrl = new URL("/login", window.location.origin);
    loginUrl.searchParams.set("redirectedFrom", pathname);
    router.replace(loginUrl.toString());
    return null;
  }

  return <>{children}</>;
}
