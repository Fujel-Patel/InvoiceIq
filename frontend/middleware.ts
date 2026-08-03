import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  let session = null;

  try {
    if (
      process.env.NEXT_PUBLIC_IS_DEVELOPMENT === 'true' ||
      !process.env.NEXT_PUBLIC_SUPABASE_URL ||
      !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    ) {
      session = { user: { id: 'dev-user-id' } } as any;
    } else {
      const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        {
          cookies: {
            getAll() {
              return request.cookies.getAll()
            },
            setAll(cookiesToSet) {
              cookiesToSet.forEach(({ name, value }) =>
                request.cookies.set(name, value)
              )
              response = NextResponse.next({
                request,
              })
              cookiesToSet.forEach(({ name, value, options }) =>
                response.cookies.set(name, value, options)
              )
            },
          },
        }
      )

      const { data } = await supabase.auth.getSession();
      session = data.session;
    }
  } catch {
    // Any middleware failure (missing env, supabase unreachable) must never
    // 500 the app — fall back to unauthenticated / dev behavior.
    session = null;
  }

  const protectedPaths = ['/history', '/result', '/settings', '/analytics'];
  const authPaths = ['/login', '/signup'];

  const isAuthPath = authPaths.includes(request.nextUrl.pathname);
  const isProtectedPath = protectedPaths.some((path) => request.nextUrl.pathname === path || request.nextUrl.pathname.startsWith(path + '/'));

  if (!session && isProtectedPath) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = '/login';
    redirectUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname);
    return NextResponse.redirect(redirectUrl);
  }

  // In dev mode the client keeps a fake in-memory session that the middleware
  // cannot see, so never bounce users off /login or /signup here.
  const hasRealSession = process.env.NEXT_PUBLIC_IS_DEVELOPMENT !== 'true' && session;
  if (hasRealSession && isAuthPath) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return response
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
};
