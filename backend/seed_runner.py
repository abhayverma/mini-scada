import time
import os
from alembic.config import Config
from alembic import command
from app.db.database import SessionLocal
from app.db.seed import seed_db

def main():
    print("⏳ Waiting 5 seconds for TimescaleDB to initialize...", flush=True)
    time.sleep(5)

    print("🚀 Running Alembic Migrations...", flush=True)
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Database schema created successfully.", flush=True)
    except Exception as e:
        print(f"❌ Migration failed: {e}", flush=True)
        return

    print("🌱 Seeding default users...", flush=True)
    db = SessionLocal()
    try:
        seed_db(db)
        print("✅ Database seeding complete.", flush=True)
    except Exception as e:
        print(f"❌ Seeding failed: {e}", flush=True)
    finally:
        db.close()

if __name__ == "__main__":
    main()