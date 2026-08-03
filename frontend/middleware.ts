import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  // This middleware must never crash the app (it runs on every matching route).
  // Real auth is enforced by the backend, which has a dev auth bypass when
  // NEXT_PUBLIC_IS_DEVELOPMENT=true. Avoid importing @supabase/ssr here — it is
  // not reliable on Vercel's Edge runtime and a middleware failure 500s the site.

  // Dev mode (or missing Supabase env) -> no-op, never redirect.
  const isDev =
    process.env.NEXT_PUBLIC_IS_DEVELOPMENT === 'true' ||
    !process.env.NEXT_PUBLIC_SUPABASE_URL ||
    !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  if (isDev) {
    return NextResponse.next()
  }

  // Production: a Supabase session is present when the browser holds sb-* cookies.
  const hasSessionCookie = request.cookies
    .getAll()
    .some((cookie) => cookie.name.startsWith('sb-'))

  const protectedPaths = ['/history', '/result', '/settings', '/analytics']
  const isProtectedPath = protectedPaths.some(
    (path) =>
      request.nextUrl.pathname === path ||
      request.nextUrl.pathname.startsWith(path + '/')
  )

  if (!hasSessionCookie && isProtectedPath) {
    const redirectUrl = request.nextUrl.clone()
    redirectUrl.pathname = '/login'
    redirectUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname)
    return NextResponse.redirect(redirectUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/',
    '/history/:path*',
    '/result/:path*',
    '/settings',
    '/analytics',
    '/login',
    '/signup',
  ],
}
