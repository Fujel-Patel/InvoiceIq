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

  if (process.env.NEXT_PUBLIC_IS_DEVELOPMENT === 'true') {
    session = { user: { id: 'dev-user-id' } } as any;
  } else {
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
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

    try {
      const { data } = await supabase.auth.getSession();
      session = data.session;
    } catch {
      // Supabase unreachable — allow request through (backend has dev auth bypass)
    }
  }

  const protectedPaths = ['/history', '/result', '/settings'];
  const authPaths = ['/login', '/signup'];

  const isAuthPath = authPaths.includes(request.nextUrl.pathname);
  const isProtectedPath = protectedPaths.some((path) => request.nextUrl.pathname === path || request.nextUrl.pathname.startsWith(path + '/'));

  if (!session && isProtectedPath) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = '/login';
    redirectUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname);
    return NextResponse.redirect(redirectUrl);
  }

  if (session && isAuthPath) {
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
    '/login',
    '/signup',
  ],
};
