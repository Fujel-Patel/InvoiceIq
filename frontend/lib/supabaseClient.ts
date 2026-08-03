import { createBrowserClient } from '@supabase/ssr'

const isDev = process.env.NEXT_PUBLIC_IS_DEVELOPMENT === 'true'

let devSignedOut = false

function createDevClient() {
  const noop = () => ({ data: { session: null }, error: null })
  const noopSubscription = { unsubscribe: () => {} }
  const fakeSession = {
    access_token: 'dev-mode-token',
    user: { id: 'dev-user-id', email: 'dev@localhost' },
  }
  return {
    auth: {
      getSession: () => ({ data: { session: devSignedOut ? null : fakeSession }, error: null }),
      onAuthStateChange: () => ({ data: { subscription: noopSubscription } }),
      signOut: () => {
        devSignedOut = true
        return noop()
      },
      signInWithPassword: async () => {
        devSignedOut = false
        return { data: { session: fakeSession, user: fakeSession.user }, error: null }
      },
      signUp: async () => {
        devSignedOut = false
        return { data: { session: fakeSession, user: fakeSession.user }, error: null }
      },
    },
  } as any
}

export function createClient() {
  if (isDev) return createDevClient()
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

export const supabase = createClient()
