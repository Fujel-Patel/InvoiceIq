import { createBrowserClient } from '@supabase/ssr'

const isDev = process.env.NEXT_PUBLIC_IS_DEVELOPMENT === 'true'

interface DevSession {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
  user: { id: string; email: string }
}

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

function createDevClient(): ReturnType<typeof createBrowserClient> {
  const noop = () => ({ data: { session: null }, error: null })
  const noopSubscription = { unsubscribe: () => {} }
  let session: DevSession | null = null
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
        return { data: { session, user }, error: null }
      },
      signOut: () => {
        session = null
        return noop()
      },
      signInWithPassword: async () => {
        session = fakeSession
        return { data: { session, user: fakeSession.user }, error: null }
      },
      signUp: async () => {
        session = fakeSession
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
