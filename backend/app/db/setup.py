from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client


def setup_database() -> bool:
    """Set up the database tables and triggers.
    Returns True on success, False on failure.
    """
    # Load environment variables
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_service_role_key:
        logger.error("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment")
        return False

    try:
        supabase: Client = create_client(supabase_url, supabase_service_role_key)
        logger.info("Connected to Supabase")
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return False

    # SQL commands to execute
    sql_commands = [
        # Create extractions table
        """
        CREATE TABLE IF NOT EXISTS extractions (
          id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id        TEXT NOT NULL,
          filename       TEXT NOT NULL,
          status         TEXT NOT NULL DEFAULT 'pending',
          vendor_name    TEXT,
          invoice_number TEXT,
          invoice_date   TEXT,
          due_date       TEXT,
          subtotal       FLOAT,
          tax            FLOAT,
          total_amount   FLOAT,
          currency       TEXT,
          entry_type     TEXT,
          amount_paid    FLOAT,
          full_data      JSONB NOT NULL,
          created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at     TIMESTAMP WITH TIME ZONE
        );
        """,
        # Create index on user_id
        """
        CREATE INDEX IF NOT EXISTS idx_extractions_user_id
        ON extractions(user_id);
        """,
        # Create update_updated_at function
        """
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
        # Create trigger to update updated_at column
        """
        CREATE OR REPLACE TRIGGER set_updated_at
        BEFORE UPDATE ON extractions
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at();
        """
    ]

    # Execute each SQL command using rpc to call exec_sql function
    for i, sql in enumerate(sql_commands, 1):
        try:
            # Remove leading/trailing whitespace and ensure no trailing semicolon (as we'll add it in the function if needed)
            sql_clean = sql.strip()
            if sql_clean.endswith(';'):
                sql_clean = sql_clean[:-1]

            # Call the exec_sql function (must be created in the database first)
            supabase.rpc('exec_sql', {'sql': sql_clean}).execute()
            logger.info(f"SQL command {i} executed successfully")
        except Exception as e:
            error_msg = str(e)
            # Check if it's because the function doesn't exist
            if 'Could not find the function' in error_msg and 'exec_sql' in error_msg:
                logger.error(
                    "The 'exec_sql' function does not exist in the database. Please create it first:\n"
                    "CREATE OR REPLACE FUNCTION exec_sql(sql text)\n"
                    "RETURNS void AS $$\n"
                    "BEGIN\n"
                    "  EXECUTE sql;\n"
                    "END;\n"
                    "$$ LANGUAGE plpgsql;\n"
                    "Then run the setup script again."
                )
                return False
            else:
                logger.error(f"Failed to execute SQL command {i}: {e}")
                return False

    logger.info("Database setup completed successfully.")
    return True

if __name__ == "__main__":
    if setup_database():
        sys.exit(0)
    else:
        sys.exit(1)
