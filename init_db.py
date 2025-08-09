#!/usr/bin/env python3
"""
Database initialization script
"""
import asyncio
import asyncpg
from app.core.config import settings

async def init_database():
    """Initialize database with required ENUM types and tables"""
    
    # Connect to database
    conn = await asyncpg.connect(
        host=settings.POSTGRES_SERVER,
        port=5432,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB
    )
    
    try:
        # Check if public schema exists, create if not
        print("Checking/creating public schema...")
        try:
            await conn.execute("CREATE SCHEMA IF NOT EXISTS public;")
            print("✓ Public schema ensured")
        except Exception as e:
            print(f"Schema creation note: {e}")
        
        print("Setting search path to public...")
        await conn.execute("SET search_path TO public;")
        
        print("Creating ENUM types...")
        
        # Create LoginProvider enum
        try:
            await conn.execute("""
                CREATE TYPE public.loginprovider AS ENUM ('LOCAL', 'NAVER', 'GOOGLE', 'KAKAO');
            """)
            print("✓ Created loginprovider enum")
        except asyncpg.DuplicateObjectError:
            print("- loginprovider enum already exists")
        
        # Create Priority enum
        try:
            await conn.execute("""
                CREATE TYPE public.priority AS ENUM ('URGENT', 'HIGH', 'MID', 'MEDIUM', 'LOW');
            """)
            print("✓ Created priority enum")
        except asyncpg.DuplicateObjectError:
            print("- priority enum already exists")
            
        # Create TaskStatus enum
        try:
            await conn.execute("""
                CREATE TYPE public.taskstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
            """)
            print("✓ Created taskstatus enum")
        except asyncpg.DuplicateObjectError:
            print("- taskstatus enum already exists")
        
        print("ENUM types created successfully!")
        
    finally:
        await conn.close()

async def create_tables():
    """Create all tables using SQLAlchemy"""
    from app.db.database import engine, Base
    from app.models import user, task
    
    print("Creating tables with SQLAlchemy...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("All tables created successfully!")
    await engine.dispose()

async def main():
    """Main initialization function"""
    try:
        await init_database()
        await create_tables()
        print("✅ Database initialization completed!")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())