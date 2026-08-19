# InvoiceIQ - Production Deployment Guide

## Overview
This guide covers deploying InvoiceIQ with custom JWT authentication to production.

**Architecture:**
- **Frontend**: Vercel (Next.js 15)
- **Backend**: Render (FastAPI)
- **Database**: Supabase (PostgreSQL)

---

## Prerequisites

- [ ] Supabase project created with PostgreSQL
- [ ] Vercel account connected to GitHub repo
- [ ] Render account connected to GitHub repo
- [ ] Domain configured (optional)

---

## Step 1: Database Setup (Supabase)

### 1.1 Run Migration
```bash
# Option A: Run SQL directly in Supabase SQL Editor
# Copy contents of backend/migrations/001_custom_auth_migration.sql

# Option B: Run Python migration script
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres"
cd backend
python -m migrations.migrate_to_custom_auth
```

### 1.2 Verify Tables Created
```sql
-- In Supabase SQL Editor
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name IN ('users', 'refresh_tokens');
```

---

## Step 2: Backend Deployment (Render)

### 2.1 Create Render Web Service
1. New → Web Service → Connect GitHub repo
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.2 Environment Variables (Render Dashboard)

| Variable | Value | Required |
|----------|-------|----------|
| `JWT_SECRET_KEY` | `openssl rand -hex 32` | ✅ |
| `JWT_ALGORITHM` | `HS256` | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | ✅ |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | ✅ |
| `BCRYPT_ROUNDS` | `12` | ✅ |
| `FRONTEND_URL` | `https://your-app.vercel.app` | ✅ |
| `SECRET_KEY` | `openssl rand -hex 32` | ✅ |
| `IS_DEVELOPMENT` | `false` | ✅ |
| `EMAIL_CONFIRMATION_REQUIRED` | `false` | ✅ |
| `DATABASE_URL` | `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres` | ✅ |
| `ANTHROPIC_API_KEY` | Your Claude API key | ✅ |
| `GEMINI_API_KEY` | Your Gemini API key | ✅ |
| `GROQ_API_KEY` | Your Groq API key | ✅ |
| `DEFAULT_LLM_PROVIDER` | `anthropic` | ✅ |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` | ✅ |
| `MAX_FILE_SIZE_MB` | `10` | ✅ |

### 2.3 Legacy Variables (REMOVE after verifying migration works)
| Variable | Action |
|----------|--------|
| `SUPABASE_URL` | Remove after migration |
| `SUPABASE_KEY` | Remove after migration |
| `SUPABASE_SERVICE_ROLE_KEY` | Remove after migration |
| `SUPABASE_JWT_SECRET` | Remove after migration |

---

## Step 3: Frontend Deployment (Vercel)

### 3.1 Create Vercel Project
1. New Project → Import GitHub repo
2. Framework: Next.js
3. Root Directory: `frontend`

### 3.2 Environment Variables (Vercel Dashboard)

| Variable | Value | Required |
|----------|-------|----------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://your-backend.onrender.com/api/v1` | ✅ |
| `NEXT_PUBLIC_IS_DEVELOPMENT` | `false` | ✅ |
| `NEXT_PUBLIC_SUPABASE_URL` | **REMOVE** - no longer needed | ❌ |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | **REMOVE** - no longer needed | ❌ |

---

## Step 4: Supabase Configuration

### 4.1 Disable Supabase Auth (Optional)
Since we're using custom auth, you can disable Supabase Auth:
1. Supabase Dashboard → Authentication → Providers
2. Disable all providers
3. Or keep enabled for other projects

### 4.2 Database Permissions
Ensure the PostgreSQL user has permissions on:
- `users` table (SELECT, INSERT, UPDATE)
- `refresh_tokens` table (SELECT, INSERT, UPDATE, DELETE)
- `extractions` table (SELECT, INSERT, UPDATE)
- `llm_configs` table (SELECT, INSERT, UPDATE, DELETE)

---

## Step 5: Verify Deployment

### 5.1 Backend Health Check
```bash
curl https://your-backend.onrender.com/health
# Expected: {"status": "ok"}
```

### 5.2 Auth Endpoints Test
```bash
# Signup
curl -X POST https://your-backend.onrender.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'

# Login
curl -X POST https://your-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123"}'

# Check cookies are set (HttpOnly, Secure, SameSite=Lax)
```

### 5.3 Frontend Test
1. Visit `https://your-app.vercel.app`
2. Should redirect to `/login`
3. Sign up → should redirect to `/`
4. Check browser DevTools → Application → Cookies
   - `access_token` (HttpOnly, Secure, 15 min)
   - `refresh_token` (HttpOnly, Secure, 7 days)

---

## Step 6: Post-Deployment Cleanup

### 6.1 Remove Legacy Code (Optional)
```bash
# Backend - remove after verification
- backend/app/services/auth_service.py (old Supabase version)
- backend/app/api/v1/auth.py (old version - replaced)
- backend/app/utils/auth.py (old version - replaced)

# Frontend - remove after verification
- Any remaining @supabase imports
```

### 6.2 Clean Up Environment Variables
Remove from Render/Vercel:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized on protected routes | Check `JWT_SECRET_KEY` matches on backend; verify cookies are sent (`withCredentials: true`) |
| CORS errors | Ensure `CORS_ORIGINS` includes frontend URL exactly (with https) |
| Cookies not set | Check `secure: true` only in production; `sameSite: "lax"` |
| Token refresh loop | Check `REFRESH_TOKEN_EXPIRE_DAYS` and rotation logic |
| Database connection failed | Verify `DATABASE_URL` format; check Supabase IP allowlist |

### Debug Commands
```bash
# Check backend logs
render logs your-backend --tail 100

# Check frontend build
vercel logs your-app

# Test database connection
psql "postgresql://postgres:pass@host:5432/db" -c "SELECT * FROM users;"
```

---

## Rollback Plan

If issues arise:

1. **Quick rollback**: Revert Vercel/Render deployments to previous version
2. **Database**: Migration is additive (new tables only), no data loss
3. **Feature flag**: Set `IS_DEVELOPMENT=true` temporarily to bypass auth

---

## Security Checklist

- [ ] `JWT_SECRET_KEY` is 32+ random bytes (not the dev value)
- [ ] `FRONTEND_URL` matches exactly (including https)
- [ ] `CORS_ORIGINS` only includes production frontend
- [ ] Cookies are HttpOnly, Secure, SameSite=Lax
- [ ] Access tokens expire in 15 minutes
- [ ] Refresh tokens rotate on use (old revoked)
- [ ] Passwords hashed with bcrypt (12+ rounds)
- [ ] Rate limiting on auth endpoints (consider adding)
- [ ] HTTPS enforced everywhere