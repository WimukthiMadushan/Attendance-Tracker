#!/usr/bin/env python3
"""
Database Migration and Schema Synchronization Script.
Executes SQL migrations with PostgreSQL connection pooling and synchronizes Prisma client.
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

# Load backend environment variables
load_dotenv(BACKEND_DIR / ".env")


async def apply_sql_migrations():
    """Apply all .sql files in backend/migrations directory in sorted order."""
    migrations_dir = BACKEND_DIR / "migrations"
    if not migrations_dir.exists():
        print(f"No migrations directory found at {migrations_dir}")
        return

    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        print("No SQL migration files found.")
        return

    from app.core.database import db_client

    print("\n" + "=" * 60)
    print("Executing SQL Migration Files")
    print("=" * 60)

    await db_client.connect()
    try:
        for sql_file in sql_files:
            print(f"Applying migration: {sql_file.name}...")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # Execute the migration script using the connection pool
            await db_client.execute(sql_content)
            print(f"  [OK] Applied {sql_file.name} successfully.")
    finally:
        await db_client.disconnect()


def sync_prisma_client():
    """Ensure Prisma schema is synchronized and Python client is generated."""
    print("\n" + "=" * 60)
    print("Synchronizing Prisma Schema & Generating Client")
    print("=" * 60)

    schema_path = BACKEND_DIR / "prisma" / "schema.prisma"
    if not schema_path.exists():
        print(f"Prisma schema not found at {schema_path}")
        return

    scripts_dir = str(Path(sys.executable).parent)
    env = os.environ.copy()
    if scripts_dir not in env.get("PATH", ""):
        env["PATH"] = f"{scripts_dir}{os.pathsep}{env.get('PATH', '')}"

    try:
        # Push schema definition to PostgreSQL
        subprocess.run(
            [sys.executable, "-m", "prisma", "db", "push", f"--schema={schema_path}", "--skip-generate"],
            cwd=str(BACKEND_DIR),
            env=env,
            check=True
        )
        print("Prisma schema pushed to database.")

        # Generate Python client
        subprocess.run(
            [sys.executable, "-m", "prisma", "generate", f"--schema={schema_path}"],
            cwd=str(BACKEND_DIR),
            env=env,
            check=True
        )
        print("Prisma Client generated successfully.")
    except Exception as e:
        print(f"Prisma synchronization error: {e}")


def main():
    try:
        asyncio.run(apply_sql_migrations())
        sync_prisma_client()
        print("\nAll database migrations and client generation completed successfully!")
    except Exception as e:
        print(f"\nMigration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
