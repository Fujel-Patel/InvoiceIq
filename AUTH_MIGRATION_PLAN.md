# InvoiceIQ - Custom JWT Authentication Migration Plan

## Overview
Migrate from Supabase Auth to custom JWT-based authentication with:
- **Backend**: Custom auth routes, JWT access/refresh tokens, middleware
- **Frontend**: HttpOnly cookies for tokens, Zustand state management
- **Database**: New `users` and `refresh_tokens` tables
- **Remove**: All Supabase dependencies (anon key, URL, JWT secret, GoTrue)

---

## 1. Database Schema Changes

### New Tables (PostgreSQL/Supabase)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt/argon2
    email_confirmed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Refresh tokens table (for rotation/revocation)
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,  -- SHA-256 of refresh token
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,
    user_agent TEXT,
    ip_address INET
);

-- Indexes
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Update existing tables to reference users.id instead of user_id text
ALTER TABLE extractions ADD COLUMN user_id UUID REFERENCES users(id);
ALTER TABLE llm_configs ADD COLUMN user_id UUID REFERENCES users(id);

-- Migrate existing data (run once)
-- UPDATE extractions SET user_id = (SELECT id FROM users WHERE email = 'dev@localhost' LIMIT 1) WHERE user_id = 'dev-user-id';
```

### Drop/Deprecate
- Remove `llm_configs.user_id` TEXT column after migration
- Remove Supabase auth tables (handled by Supabase, not in our schema)

---

## 2. Backend Architecture

### 2.1 Token Strategy

| Token | Lifetime | Storage | Purpose |
|-------|----------|---------|---------|
| Access Token | 15 min | HttpOnly Cookie (frontend) | API authorization |
| Refresh Token | 7 days | HttpOnly Cookie + DB (hashed) | Token rotation |

**Access Token Payload:**
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "type": "access",
  "iat": 1234567890,
  "exp": 1234568790
}
```

**Refresh Token:** Opaque random string (32 bytes), stored hashed in DB

### 2.2 New Auth Routes (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register new user, return tokens |
| POST | `/auth/login` | Validate credentials, return tokens |
| POST | `/auth/refresh` | Rotate access + refresh token |
| POST | `/auth/logout` | Revoke refresh token, clear cookies |
| POST | `/auth/forgot-password` | Request password reset email |
| POST | `/auth/reset-password` | Reset password with token |
| GET | `/auth/me` | Get current user profile |

### 2.3 Auth Middleware (`backend/app/utils/auth.py`)

```python
# New dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Validate access token from Authorization header OR cookie"""
    
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """For routes that work with or without auth"""

async def require_verified_email(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user has confirmed email"""
```

### 2.4 Services to Create/Update

| File | Responsibility |
|------|----------------|
| `services/auth_service.py` | Core auth logic (signup, login, password reset, token generation) |
| `services/token_service.py` | JWT creation, validation, refresh token rotation |
| `services/password_service.py` | bcrypt/argon2 hashing, validation |
| `services/email_service.py` | Password reset emails (optional: use Resend/SendGrid) |
| `models/auth.py` | Pydantic models for requests/responses |
| `schemas/auth.py` | API request/response schemas |
| `utils/auth.py` | FastAPI dependencies (get_current_user, etc.) |

### 2.5 Environment Variables (Backend)

```env
# Remove these:
# SUPABASE_URL
# SUPABASE_KEY
# SUPABASE_SERVICE_ROLE_KEY
# SUPABASE_JWT_SECRET

# Add these:
JWT_SECRET_KEY=your-256-bit-secret-key  # openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
EMAIL_RESET_TOKEN_EXPIRE_HOURS=1
FRONTEND_URL=https://your-frontend.vercel.app  # For CORS + email links
```

---

## 3. Frontend Architecture

### 3.1 Cookie Storage (HttpOnly, Secure, SameSite)

```typescript
// lib/cookies.ts
import { cookies } from 'next/headers'

const COOKIE_OPTIONS = {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax' as const,
  path: '/',
  maxAge: 60 * 60 * 24 * 7, // 7 days for refresh token
}

export function setAuthCookies(accessToken: string, refreshToken: string) {
  const cookieStore = cookies()
  cookieStore.set('access_token', accessToken, {
    ...COOKIE_OPTIONS,
    maxAge: 60 * 15, // 15 min
  })
  cookieStore.set('refresh_token', refreshToken, COOKIE_OPTIONS)
}

export function clearAuthCookies() {
  const cookieStore = cookies()
  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
}

export function getAccessToken(): string | undefined {
  return cookies().get('access_token')?.value
}

export function getRefreshToken(): string | undefined {
  return cookies().get('refresh_token')?.value
}
```

### 3.2 Zustand Auth Store (`store/useAuthStore.ts`)

```typescript
interface User {
  id: string
  email: string
  emailConfirmed: boolean
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
  hydrate: () => Promise<void>  // Call on app init
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: true,
      isAuthenticated: false,
      
      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user, 
        isLoading: false 
      }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      logout: () => set({ user: null, isAuthenticated: false }),
      
      hydrate: async () => {
        try {
          const res = await fetch('/api/auth/me')
          if (res.ok) {
            const data = await res.json()
            set({ user: data.user, isAuthenticated: true, isLoading: false })
          } else {
            set({ user: null, isAuthenticated: false, isLoading: false })
          }
        } catch {
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
```

### 3.3 API Client (`lib/api.ts`)

```typescript
// No more supabase client - use fetch with credentials
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  withCredentials: true,  // Critical: sends cookies automatically
})

// Auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        await refreshAccessToken()
        return api(originalRequest)
      } catch {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

async function refreshAccessToken() {
  const res = await fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) throw new Error('Refresh failed')
}
```

### 3.4 Auth Pages (Client Components)

| Page | Changes |
|------|---------|
| `/login` | Call `/api/v1/auth/login`, cookies set by backend |
| `/signup` | Call `/api/v1/auth/signup` |
| `/forgot-password` | Call `/api/v1/auth/forgot-password` |
| `/reset-password` | Call `/api/v1/auth/reset-password` |
| `/settings` | Use `useAuthStore` for user data |

### 3.5 Middleware (`middleware.ts`)

```typescript
// Refresh session on each request for Server Components
export async function middleware(request: NextRequest) {
  const response = NextResponse.next()
  
  // Check if access token exists and is valid
  const accessToken = request.cookies.get('access_token')?.value
  const refreshToken = request.cookies.get('refresh_token')?.value
  
  if (!accessToken && refreshToken) {
    // Try to refresh
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { Cookie: `refresh_token=${refreshToken}` },
    })
    if (res.ok) {
      const { access_token, refresh_token } = await res.json()
      response.cookies.set('access_token', accessToken, { ... })
      response.cookies.set('refresh_token', refreshToken, { ... })
    }
  }
  
  return response
}
```

---

## 4. Migration Steps

### Phase 1: Backend Foundation (Week 1)
- [ ] Create new database tables (users, refresh_tokens)
- [ ] Implement password hashing service (bcrypt)
- [ ] Implement JWT token service (access + refresh)
- [ ] Create auth Pydantic models/schemas
- [ ] Write unit tests for auth service

### Phase 2: Backend Auth Routes (Week 1-2)
- [ ] POST `/auth/signup`
- [ ] POST `/auth/login`
- [ ] POST `/auth/refresh` (with token rotation)
- [ ] POST `/auth/logout`
- [ ] POST `/auth/forgot-password`
- [ ] POST `/auth/reset-password`
- [ ] GET `/auth/me`
- [ ] Update `get_current_user` dependency
- [ ] Integration tests for all routes

### Phase 3: Frontend Cookie & State (Week 2)
- [ ] Remove `@supabase/ssr`, `@supabase/auth-helpers-nextjs`
- [ ] Implement cookie utilities
- [ ] Create Zustand auth store with persist
- [ ] Update `lib/api.ts` for cookie-based auth
- [ ] Add auto-refresh interceptor
- [ ] Update login/signup/forgot/reset pages
- [ ] Update middleware.ts for session refresh

### Phase 4: Protected Routes & Integration (Week 2-3)
- [ ] Update all protected API routes to use new `get_current_user`
- [ ] Update `extractions`, `llm_configs` to use UUID user_id
- [ ] Migrate existing user data (dev user)
- [ ] Test full auth flow: signup -> login -> refresh -> logout

### Phase 5: Cleanup & Deploy (Week 3)
- [ ] Remove Supabase client from frontend
- [ ] Remove Supabase auth service from backend
- [ ] Remove Supabase env vars from Vercel/Render
- [ ] Update CORS origins
- [ ] Deploy to staging -> production
- [ ] Monitor for 401s, token refresh issues

---

## 5. Rollback Strategy

| Scenario | Rollback Action |
|----------|-----------------|
| Critical bug in production | Revert Vercel/Render deploy, keep DB migrations (additive only) |
| Token refresh loops | Feature flag to disable auto-refresh, force re-login |
| DB migration issues | Migration is additive (new tables only), no data loss risk |

---

## 6. Security Considerations

- **Access tokens**: Short-lived (15 min), in HttpOnly cookie
- **Refresh tokens**: Long-lived (7 days), hashed in DB, rotated on use
- **Token rotation**: Issue new refresh token on each refresh, revoke old
- **Logout**: Revoke refresh token in DB + clear cookies
- **Password reset**: Time-limited (1 hour), single-use tokens
- **Rate limiting**: Apply to auth endpoints (signup, login, refresh)
- **CORS**: Restrict to frontend domain only

---

## 7. Files to Create/Modify

### Backend (New)
```
backend/app/
├── models/
│   ├── user.py              # SQLAlchemy User model
│   └── refresh_token.py     # SQLAlchemy RefreshToken model
├── schemas/
│   └── auth.py              # Pydantic request/response models
├── services/
│   ├── auth_service.py      # Core auth logic
│   ├── token_service.py     # JWT create/validate
│   ├── password_service.py  # bcrypt hash/verify
│   └── email_service.py     # Password reset emails
├── api/v1/
│   └── auth.py              # Auth routes
├── utils/
│   └── auth.py              # FastAPI dependencies (updated)
└── db/
    └── migrations/
        └── 001_create_auth_tables.py
```

### Backend (Modified)
- `backend/app/main.py` - Remove Supabase auth router, add new auth router
- `backend/app/core/config.py` - New env vars, remove Supabase vars
- `backend/app/api/v1/extract.py` - Update `get_current_user` import
- `backend/app/api/v1/history.py` - Same
- `backend/app/api/v1/llm_config.py` - Same
- `backend/app/services/llm_config_service.py` - Use UUID user_id

### Frontend (New)
```
frontend/
├── lib/
│   ├── cookies.ts           # Cookie utilities
│   └── api.ts               # Updated axios instance
├── store/
│   └── useAuthStore.ts      # Zustand auth store
├── app/
│   ├── api/
│   │   └── auth/
│   │       ├── me/route.ts      # GET /api/auth/me (proxy to backend)
│   │       ├── refresh/route.ts # POST /api/auth/refresh (proxy)
│   │       └── logout/route.ts  # POST /api/auth/logout (proxy)
│   └── components/
│       └── AuthProvider.tsx     # Client provider for auth hydration
```

### Frontend (Modified)
- `frontend/middleware.ts` - Session refresh logic
- `frontend/app/login/page.tsx` - New login flow
- `frontend/app/signup/page.tsx` - New signup flow
- `frontend/app/forgot-password/page.tsx` - New flow
- `frontend/app/reset-password/page.tsx` - New flow
- `frontend/app/page.tsx` - Use `useAuthStore` instead of supabase check
- `frontend/components/Header.tsx` - Use `useAuthStore`
- `frontend/package.json` - Remove supabase packages

---

## 8. Testing Checklist

- [ ] Signup -> email confirmation -> login works
- [ ] Login -> access token expires -> auto-refresh works
- [ ] Refresh token rotation (old token revoked)
- [ ] Logout -> tokens cleared -> cannot access protected routes
- [ ] Concurrent logins (multiple devices) work independently
- [ ] Password reset flow works end-to-end
- [ ] Protected API routes return 401 without valid token
- [ ] CORS works from frontend domain only
- [ ] Rate limiting prevents brute force