#!/usr/bin/env python3
"""
Clear all data from the database for fresh testing
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://potenday:potenday123@localhost/potendaydb")

async def clear_database():
    """Clear all data from database tables"""
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("=" * 60)
    print("DATABASE CLEANUP")
    print("=" * 60)
    
    async with async_session() as session:
        try:
            # Get all table names (excluding alembic version table)
            result = await session.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename != 'alembic_version'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result]
            
            print(f"\n📋 Found {len(tables)} tables to clear:")
            for table in tables:
                print(f"  - {table}")
            
            # Clear data from each table
            print("\n🗑️ Clearing data...")
            for table in reversed(tables):  # Reverse order to handle foreign keys
                try:
                    await session.execute(text(f"DELETE FROM {table}"))
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  ✓ {table}: cleared (now {count} rows)")
                except Exception as e:
                    print(f"  ✗ {table}: {e}")
            
            await session.commit()
            print("\n✅ Database cleared successfully!")
            
            # Show current status
            print("\n📊 Current database status:")
            for table in tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} rows")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()
    
    print("\n" + "=" * 60)
    print("Database is ready for fresh testing!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(clear_database())