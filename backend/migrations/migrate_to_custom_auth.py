#!/usr/bin/env python3
"""
InvoiceIQ - Custom Auth Migration Script

This script migrates the database from Supabase Auth to custom JWT authentication.
It creates the new users and refresh_tokens tables, and migrates existing data.

Run: python -m backend.migrations.migrate_to_custom_auth
"""

from __future__ import annotations

import os
import sys
import uuid
import bcrypt
from datetime import datetime, timezone

# Add repo root to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.core.database import Base
from backend.app.models.user import User
from backend.app.models.refresh_token import RefreshToken
from backend.app.models.extraction import Extraction


def get_database_url() -> str:
    """Get database URL from environment or config."""
    # Try to get from environment first (for production)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Fallback to Supabase URL from config
    if settings.SUPABASE_URL:
        # Convert Supabase URL to PostgreSQL connection string
        # This assumes you have the connection string in SUPABASE_DB_URL or similar
        return os.getenv("SUPABASE_DB_URL", "")

    raise ValueError("No database URL found. Set DATABASE_URL or SUPABASE_DB_URL environment variable.")


def create_tables(engine) -> None:
    """Create new tables for custom auth."""
    print("Creating custom auth tables...")
    Base.metadata.create_all(engine, tables=[User.__table__, RefreshToken.__table__])
    print("  ✓ users table created")
    print("  ✓ refresh_tokens table created")


def migrate_existing_data(session) -> None:
    """Migrate existing extractions and llm_configs to use UUID user_id."""
    print("Migrating existing data...")

    # Create or get dev user
    dev_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    dev_user = session.query(User).filter(User.id == dev_user_id).first()

    if not dev_user:
        print("  Creating dev user...")
        password_hash = bcrypt.hashpw(b"password", bcrypt.gensalt(rounds=12)).decode("utf-8")
        dev_user = User(
            id=dev_user_id,
            email="dev@localhost",
            password_hash=password_hash,
            email_confirmed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(dev_user)
        session.commit()
        print("  ✓ Dev user created")
    else:
        print("  ✓ Dev user already exists")

    # Update extractions to use UUID user_id
    print("  Updating extractions...")
    extractions = session.query(Extraction).filter(Extraction.user_id_uuid.is_(None)).all()
    for extraction in extractions:
        extraction.user_id_uuid = dev_user_id
    session.commit()
    print(f"  ✓ Updated {len(extractions)} extractions")

    # Note: llm_configs migration would go here if needed
    print("  ✓ Data migration complete")


def create_dev_refresh_token(session) -> None:
    """Create a dev refresh token for testing."""
    print("Creating dev refresh token...")
    dev_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    import hashlib
    import secrets

    refresh_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc).replace(year=datetime.now().year + 1)

    existing = session.query(RefreshToken).filter(
        RefreshToken.user_id == dev_user_id,
        RefreshToken.revoked_at.is_(None)
    ).first()

    if not existing:
        refresh_token_obj = RefreshToken(
            user_id=dev_user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent="dev-migration-script",
            ip_address="127.0.0.1",
        )
        session.add(refresh_token_obj)
        session.commit()
        print(f"  ✓ Dev refresh token created: {refresh_token[:20]}...")
    else:
        print("  ✓ Dev refresh token already exists")


def verify_migration(session) -> None:
    """Verify migration completed successfully."""
    print("\nVerifying migration...")

    user_count = session.query(User).count()
    token_count = session.query(RefreshToken).count()
    extraction_count = session.query(Extraction).filter(Extraction.user_id_uuid.isnot(None)).count()

    print(f"  Users: {user_count}")
    print(f"  Refresh tokens: {token_count}")
    print(f"  Extractions with UUID user_id: {extraction_count}")

    # Check dev user exists
    dev_user = session.query(User).filter(User.id == uuid.UUID("00000000-0000-0000-0000-000000000001")).first()
    if dev_user:
        print(f"  ✓ Dev user: {dev_user.email}")
    else:
        print("  ✗ Dev user missing!")


def main() -> int:
    """Run the migration."""
    print("=" * 60)
    print("InvoiceIQ Custom Auth Migration")
    print("=" * 60)

    try:
        db_url = get_database_url()
        if not db_url:
            print("ERROR: No database URL configured.")
            print("Set DATABASE_URL environment variable.")
            return 1

        # Mask password in output
        masked_url = db_url
        if "@" in db_url:
            parts = db_url.split("@")
            masked_url = parts[0].split(":")[0] + ":***@" + parts[1]
        print(f"Connecting to: {masked_url}")

        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Run migration steps
        create_tables(engine)
        migrate_existing_data(session)
        create_dev_refresh_token(session)
        verify_migration(session)

        session.close()
        engine.dispose()

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())