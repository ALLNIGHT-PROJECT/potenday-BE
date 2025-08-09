#!/usr/bin/env python3
"""
Script to update bio field length in database
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def update_bio_field():
    # Get database connection details from environment
    conn = await asyncpg.connect(
        host=os.getenv("POSTGRES_SERVER"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB")
    )
    
    try:
        # Update the bio column to allow 500 characters
        await conn.execute("ALTER TABLE users ALTER COLUMN bio TYPE VARCHAR(500)")
        print("Successfully updated bio field to VARCHAR(500)")
    except Exception as e:
        print(f"Error updating bio field: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(update_bio_field())