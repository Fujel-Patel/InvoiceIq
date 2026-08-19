import { createBrowserClient } from '@supabase/ssr'

const isDev = process.env.NEXT_PUBLIC_IS_DEVELOPMENT === 'true'

interface DevSession {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
  user: { id: string; email: string }
}

const DEV_SESSION_KEY = 'invoiceiq-dev-session'

function decodeJwtUser(token: string): { id: string; email: string } {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(window.atob(base64))
    return {
      id: typeof payload.sub === 'string' ? payload.sub : 'dev-user-id',
      email: typeof payload.email === 'string' ? payload.email : 'dev@localhost',
    }
  } catch {
    return { id: 'dev-user-id', email: 'dev@localhost' }
  }
}

function loadDevSession(): DevSession | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem(DEV_SESSION_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (parsed.access_token && parsed.user) {
        return parsed as DevSession
      }
    }
  } catch {
    // Ignore parse errors
  }
  return null
}

function saveDevSession(session: DevSession | null) {
  if (typeof window === 'undefined') return
  if (session) {
    localStorage.setItem(DEV_SESSION_KEY, JSON.stringify(session))
  } else {
    localStorage.removeItem(DEV_SESSION_KEY)
  }
}

function createDevClient(): ReturnType<typeof createBrowserClient> {
  const noop = () => ({ data: { session: null }, error: null })
  const noopSubscription = { unsubscribe: () => {} }
  let session: DevSession | null = loadDevSession()
  const fakeSession: DevSession = {
    access_token: 'dev-mode-token',
    refresh_token: 'dev-mode-refresh',
    expires_in: 3600,
    token_type: 'bearer',
    user: { id: 'dev-user-id', email: 'dev@localhost' },
  }
  return {
    auth: {
      getSession: () => ({ data: { session }, error: null }),
      getUser: () => ({ data: { user: session?.user ?? null }, error: null }),
      onAuthStateChange: () => ({ data: { subscription: noopSubscription } }),
      setSession: async (currentSession: { access_token: string; refresh_token: string }) => {
        const user = decodeJwtUser(currentSession.access_token)
        session = {
          access_token: currentSession.access_token,
          refresh_token: currentSession.refresh_token,
          expires_in: 3600,
          token_type: 'bearer',
          user,
        }
        saveDevSession(session)
        return { data: { session, user }, error: null }
      },
      signOut: () => {
        session = null
        saveDevSession(null)
        return noop()
      },
      signInWithPassword: async () => {
        session = fakeSession
        saveDevSession(session)
        return { data: { session, user: fakeSession.user }, error: null }
      },
      signUp: async () => {
        session = fakeSession
        saveDevSession(session)
        return { data: { session, user: fakeSession.user }, error: null }
      },
    },
  } as unknown as ReturnType<typeof createBrowserClient>
}

export function createClient() {
  if (isDev) return createDevClient()
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

export const supabase = createClient()
