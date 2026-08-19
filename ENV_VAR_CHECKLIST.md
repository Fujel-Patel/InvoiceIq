# InvoiceIQ - Environment Variables Checklist

## Quick Reference

| Variable | Backend (Render) | Frontend (Vercel) | Description |
|----------|------------------|-------------------|-------------|
| `JWT_SECRET_KEY` | ✅ Required | ❌ | 32+ byte random secret for JWT signing |
| `JWT_ALGORITHM` | ✅ `HS256` | ❌ | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ `15` | ❌ | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ✅ `7` | ❌ | Refresh token lifetime |
| `BCRYPT_ROUNDS` | ✅ `12` | ❌ | Password hashing cost |
| `FRONTEND_URL` | ✅ Required | ❌ | Frontend URL for CORS & email links |
| `SECRET_KEY` | ✅ Required | ❌ | App secret key |
| `IS_DEVELOPMENT` | ✅ `false` | ❌ | **Must be false in production** |
| `EMAIL_CONFIRMATION_REQUIRED` | ✅ `false` | ❌ | Email verification toggle |
| `DATABASE_URL` | ✅ Required | ❌ | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | ✅ Required | ❌ | Claude API key |
| `GEMINI_API_KEY` | ✅ Required | ❌ | Gemini API key |
| `GROQ_API_KEY` | ✅ Required | ❌ | Groq API key |
| `DEFAULT_LLM_PROVIDER` | ✅ `anthropic` | ❌ | Default LLM provider |
| `CORS_ORIGINS` | ✅ Required | ❌ | `["https://your-app.vercel.app"]` |
| `MAX_FILE_SIZE_MB` | ✅ `10` | ❌ | Upload limit |
| `NEXT_PUBLIC_API_BASE_URL` | ❌ | ✅ Required | `https://your-backend.onrender.com/api/v1` |
| `NEXT_PUBLIC_IS_DEVELOPMENT` | ❌ | ✅ `false` | **Must be false in production** |

---

## Generate Secrets

```bash
# JWT_SECRET_KEY (32 bytes = 64 hex chars)
openssl rand -hex 32

# SECRET_KEY (32 bytes)
openssl rand -hex 32

# Example output: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

---

## Backend (Render) - Complete List

```env
# ============================================
# SECURITY (CRITICAL - Generate new for production!)
# ============================================
JWT_SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
SECRET_KEY=b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456a1
IS_DEVELOPMENT=false

# ============================================
# AUTH
# ============================================
EMAIL_CONFIRMATION_REQUIRED=false
FRONTEND_URL=https://your-app.vercel.app

# ============================================
# DATABASE (Supabase PostgreSQL)
# ============================================
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_REF.supabase.co:5432/postgres

# ============================================
# LLM PROVIDERS (at least one required)
# ============================================
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
GEMINI_API_KEY=AIzaSyxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxx
# OPENAI_API_KEY=sk-xxxxx (optional)
# OPENROUTER_API_KEY=sk-or-xxxxx (optional)

DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_LLM_MODEL=claude-opus-4-5-20251001
DEFAULT_LLM_API_KEY=

# ============================================
# CORS & FILE UPLOAD
# ============================================
CORS_ORIGINS=["https://your-app.vercel.app"]
MAX_FILE_SIZE_MB=10
ALLOWED_TYPES=["image/jpeg","image/png","application/pdf"]

# ============================================
# LEGACY - REMOVE AFTER MIGRATION VERIFIED
# ============================================
# SUPABASE_URL=...
# SUPABASE_KEY=...
# SUPABASE_SERVICE_ROLE_KEY=...
# SUPABASE_JWT_SECRET=...
```

---

## Frontend (Vercel) - Complete List

```env
# ============================================
# API CONFIGURATION
# ============================================
NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api/v1

# ============================================
# AUTH MODE
# ============================================
NEXT_PUBLIC_IS_DEVELOPMENT=false

# ============================================
# LEGACY - REMOVE (no longer used)
# ============================================
# NEXT_PUBLIC_SUPABASE_URL=...
# NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

---

## Pre-Deployment Verification

### Backend (Render)
- [ ] `JWT_SECRET_KEY` is 64 hex chars (32 bytes)
- [ ] `SECRET_KEY` is 64 hex chars (32 bytes)
- [ ] `IS_DEVELOPMENT=false`
- [ ] `FRONTEND_URL` matches Vercel URL exactly (https://...)
- [ ] `DATABASE_URL` uses Supabase PostgreSQL connection string
- [ ] At least one LLM API key is set
- [ ] `CORS_ORIGINS` includes only production frontend URL
- [ ] Legacy Supabase vars REMOVED

### Frontend (Vercel)
- [ ] `NEXT_PUBLIC_API_BASE_URL` matches Render backend URL + `/api/v1`
- [ ] `NEXT_PUBLIC_IS_DEVELOPMENT=false`
- [ ] Legacy Supabase vars REMOVED

---

## Post-Deployment Test

```bash
# 1. Backend health
curl https://your-backend.onrender.com/health

# 2. Signup test
curl -X POST https://your-backend.onrender.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'

# 3. Login test (check cookies)
curl -v -X POST https://your-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'

# 4. Frontend loads
open https://your-app.vercel.app
```

---

## Emergency Rollback

If auth is broken:

1. **Vercel**: Deploy previous working version
2. **Render**: Deploy previous working version
3. **Database**: No rollback needed (additive migration)
4. **Temp fix**: Set `IS_DEVELOPMENT=true` on backend to bypass auth