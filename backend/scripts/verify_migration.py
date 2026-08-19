#!/usr/bin/env python3
"""
Verify the custom auth migration works correctly.
Run this locally against your database to verify before deploying.
"""

from __future__ import annotations

import os
import sys
import uuid

# Add repo root to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.extraction import Extraction
from backend.app.services.auth_service import signup, login, get_current_user, logout
from backend.app.services.token_service import create_access_token, store_refresh_token, validate_refresh_token, rotate_refresh_token
from backend.app.services.password_service import hash_password, verify_password


def get_database_url() -> str:
    """Get database URL from environment."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Try to construct from Supabase settings
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            # This won't work directly - need actual PostgreSQL connection string
            pass
    return db_url


def verify_tables_exist(engine) -> bool:
    """Check if required tables exist."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name IN ('users', 'refresh_tokens')
        """))
        tables = [row[0] for row in result]
        print(f"Found tables: {tables}")
        return 'users' in tables and 'refresh_tokens' in tables


def verify_dev_user(session) -> bool:
    """Check if dev user exists."""
    dev_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    user = session.query(User).filter(User.id == dev_user_id).first()
    if user:
        print(f"✓ Dev user exists: {user.email}")
        return True
    print("✗ Dev user missing")
    return False


def verify_extractions_migrated(session) -> bool:
    """Check if extractions have UUID user_id."""
    count = session.query(Extraction).filter(Extraction.user_id_uuid.isnot(None)).count()
    total = session.query(Extraction).count()
    if count == total and total > 0:
        print(f"✓ All {total} extractions migrated to UUID user_id")
        return True
    elif total == 0:
        print("⚠ No extractions found (OK for fresh deploy)")
        return True
    else:
        print(f"✗ Only {count}/{total} extractions migrated")
        return False


def test_password_hashing() -> bool:
    """Test password hashing works."""
    password = "TestPassword123"
    hashed = hash_password(password)
    if verify_password(password, hashed):
        print("✓ Password hashing works")
        return True
    print("✗ Password hashing failed")
    return False


def test_token_creation() -> bool:
    """Test JWT token creation."""
    user_id = uuid.uuid4()
    email = "test@example.com"
    access_token = create_access_token(user_id, email)
    if access_token:
        print("✓ Access token creation works")
        return True
    print("✗ Access token creation failed")
    return False


def test_auth_flow(session) -> bool:
    """Test complete auth flow: signup -> login -> get_current_user -> logout."""
    try:
        # Test signup
        import asyncio
        
        async def run_test():
            test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            test_password = "TestPassword123"
            
            # Signup
            user = await signup(session, test_email, test_password)
            print(f"✓ Signup works: {user.email}")
            
            # Login
            tokens = await login(session, test_email, test_password)
            print("✓ Login works: tokens received")
            
            # Get current user
            current = await get_current_user(session, tokens.access_token)
            print(f"✓ Get current user works: {current.email}")
            
            # Logout
            result = await logout(session, tokens.refresh_token)
            print(f"✓ Logout works: {result}")
            
            return True
        
        asyncio.run(run_test())
        return True
    except Exception as e:
        print(f"✗ Auth flow failed: {e}")
        return False


def test_token_rotation(session) -> bool:
    """Test refresh token rotation."""
    try:
        import asyncio
        
        async def run_test():
            test_email = f"rotate_{uuid.uuid4().hex[:8]}@example.com"
            test_password = "TestPassword123"
            
            # Signup and login
            await signup(session, test_email, test_password)
            tokens = await login(session, test_email, test_password)
            
            # Store refresh token
            await store_refresh_token(session, uuid.UUID(tokens.user.id if hasattr(tokens, 'user') else "00000000-0000-0000-0000-000000000001"), tokens.refresh_token)
            
            # Validate refresh token
            valid_token = await validate_refresh_token(session, tokens.refresh_token)
            if not valid_token:
                print("✗ Refresh token validation failed")
                return False
            
            # Rotate refresh token
            rotated = await rotate_refresh_token(session, tokens.refresh_token)
            if not rotated:
                print("✗ Refresh token rotation failed")
                return False
            
            new_token, new_record = rotated
            print("✓ Refresh token rotation works")
            
            # Old token should be revoked
            old_valid = await validate_refresh_token(session, tokens.refresh_token)
            if old_valid:
                print("✗ Old token not revoked")
                return False
            
            print("✓ Old token properly revoked")
            return True
        
        return asyncio.run(run_test())
    except Exception as e:
        print(f"✗ Token rotation test failed: {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("InvoiceIQ Migration Verification")
    print("=" * 60)
    
    db_url = get_database_url()
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Set it to your PostgreSQL connection string:")
        print("  export DATABASE_URL='postgresql://user:pass@host:5432/db'")
        return 1
    
    # Mask password in output
    masked = db_url.split("@")[0].split(":")[0] + ":***@" + db_url.split("@")[1] if "@" in db_url else db_url
    print(f"Connecting to: {masked}")
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    all_passed = True
    
    print("\n1. Checking tables...")
    all_passed &= verify_tables_exist(engine)
    
    print("\n2. Checking dev user...")
    all_passed &= verify_dev_user(session)
    
    print("\n3. Checking extractions migration...")
    all_passed &= verify_extractions_migrated(session)
    
    print("\n4. Testing password hashing...")
    all_passed &= test_password_hashing()
    
    print("\n5. Testing token creation...")
    all_passed &= test_token_creation()
    
    print("\n6. Testing auth flow...")
    all_passed &= test_auth_flow(session)
    
    print("\n7. Testing token rotation...")
    all_passed &= test_token_rotation(session)
    
    session.close()
    engine.dispose()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Migration verified!")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Review output above")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())