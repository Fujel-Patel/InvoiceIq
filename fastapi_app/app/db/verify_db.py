import os
from dotenv import load_dotenv
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
        print(f"✅ {table} → Connected")
    except Exception as e:
        print(f"❌ {table} → FAILED: {e}")