"use client";

interface CookieOptions {
  path?: string;
  sameSite?: "strict" | "lax" | "none";
  secure?: boolean;
  maxAge?: number;
  expires?: Date;
}

const COOKIE_OPTIONS: CookieOptions = {
  path: "/",
  sameSite: "lax",
  secure: process.env.NODE_ENV === "production",
};

export const ACCESS_TOKEN_COOKIE = "access_token";
export const REFRESH_TOKEN_COOKIE = "refresh_token";

export function getCookie(name: string): string | undefined {
  if (typeof document === "undefined") return undefined;

  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(";").shift();
  }
  return undefined;
}

export function setCookie(
  name: string,
  value: string,
  options: Partial<CookieOptions> = {}
): void {
  if (typeof document === "undefined") return;

  const opts = { ...COOKIE_OPTIONS, ...options };
  let cookieString = `${name}=${value}; Path=${opts.path}; SameSite=${opts.sameSite}`;

  if (opts.maxAge) {
    cookieString += `; Max-Age=${opts.maxAge}`;
  }
  if (opts.expires) {
    cookieString += `; Expires=${opts.expires.toUTCString()}`;
  }
  if (opts.secure) {
    cookieString += `; Secure`;
  }

  document.cookie = cookieString;
}

export function deleteCookie(name: string, options: Partial<CookieOptions> = {}): void {
  if (typeof document === "undefined") return;

  const opts = { ...COOKIE_OPTIONS, ...options, maxAge: 0 };
  document.cookie = `${name}=; Path=${opts.path}; SameSite=${opts.sameSite}; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT${
    opts.secure ? "; Secure" : ""
  }`;
}

export function getAccessToken(): string | undefined {
  return getCookie(ACCESS_TOKEN_COOKIE);
}

export function getRefreshToken(): string | undefined {
  return getCookie(REFRESH_TOKEN_COOKIE);
}

export function setAuthCookies(accessToken: string, refreshToken: string): void {
  // Access token: 15 minutes
  setCookie(ACCESS_TOKEN_COOKIE, accessToken, { maxAge: 15 * 60 });
  // Refresh token: 7 days
  setCookie(REFRESH_TOKEN_COOKIE, refreshToken, { maxAge: 7 * 24 * 60 * 60 });
}

export function clearAuthCookies(): void {
  deleteCookie(ACCESS_TOKEN_COOKIE);
  deleteCookie(REFRESH_TOKEN_COOKIE);
}