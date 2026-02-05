from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Priority: Environment variable (for Kubernetes/Docker) > database.ini (for local dev)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # If URL starts with postgres://, convert to postgresql+asyncpg://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    print(f"Using DATABASE_URL from environment variable")
else:
    # Fallback to database.ini for local development
    import configparser
    from pathlib import Path
    
    config = configparser.ConfigParser()
    config_path = Path(__file__).resolve().parent / 'database.ini'
    config.read(config_path)
    
    db_user = config['postgresql']['user']
    db_password = config['postgresql']['password'] 
    db_host = config['postgresql']['host']
    db_port = config['postgresql']['port']
    database = config['postgresql']['database']
    
    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{database}"
    print(f"Using DATABASE_URL from database.ini (local development)")

print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ############## Test the database connection ###############
# async def test_connection():
#     try:
#         async with engine.connect() as conn:
#             result = await conn.execute(text("SELECT 1"))
#             print("Database connected successfully!")
#     except Exception as e:
#         print("Database connection failed:")
#         print(e)

# if __name__ == "__main__":
#     # Test the database connection
#     asyncio.run(test_connection())