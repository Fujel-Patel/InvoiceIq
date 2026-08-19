import { NextResponse, type NextRequest } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8765/api/v1';

export async function middleware(request: NextRequest) {
  const response = NextResponse.next({ request });

  // Skip auth check for public paths
  const publicPaths = ['/login', '/signup', '/forgot-password', '/reset-password'];
  const isPublicPath = publicPaths.some((path) => request.nextUrl.pathname.startsWith(path));

  // Also skip for static assets and API routes
  if (
    isPublicPath ||
    request.nextUrl.pathname.startsWith('/_next') ||
    request.nextUrl.pathname.startsWith('/api') ||
    request.nextUrl.pathname.match(/\.(svg|png|jpg|jpeg|gif|webp|ico)$/)
  ) {
    return response;
  }

  // Check if access token exists
  const accessToken = request.cookies.get('access_token')?.value;
  const refreshToken = request.cookies.get('refresh_token')?.value;

  // If no access token but has refresh token, try to refresh
  if (!accessToken && refreshToken) {
    try {
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          Cookie: `refresh_token=${refreshToken}`,
        },
      });

      if (res.ok) {
        const { access_token, refresh_token } = await res.json();
        response.cookies.set('access_token', access_token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          path: '/',
          maxAge: 15 * 60, // 15 minutes
        });
        response.cookies.set('refresh_token', refresh_token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          path: '/',
          maxAge: 7 * 24 * 60 * 60, // 7 days
        });
      } else {
        // Refresh failed, clear cookies and redirect to login
        response.cookies.delete('access_token');
        response.cookies.delete('refresh_token');
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname);
        return NextResponse.redirect(loginUrl);
      }
    } catch {
      // Network error, clear cookies and redirect to login
      response.cookies.delete('access_token');
      response.cookies.delete('refresh_token');
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname);
      return NextResponse.redirect(loginUrl);
    }
  } else if (!accessToken && !refreshToken) {
    // No tokens at all, redirect to login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirectedFrom', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return response;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)',
  ],
};