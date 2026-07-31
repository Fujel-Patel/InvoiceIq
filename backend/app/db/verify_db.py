from __future__ import annotations

import os

from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

tables = ["extractions", "llm_configs"]

for table in tables:
    try:
        result = client.table(table).select("*").limit(1).execute()
        logger.info(f"{table} -> Connected")
    except Exception as e:
        logger.error(f"{table} -> FAILED: {e}")
