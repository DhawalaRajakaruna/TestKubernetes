from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import configparser
from pathlib import Path
import asyncio
from sqlalchemy import text
import asyncpg

config = configparser.ConfigParser()
config_path = Path(__file__).resolve().parent / 'database.ini'
config.read(config_path)

db_user = config['postgresql']['user']
db_password = config['postgresql']['password'] 
db_host = config['postgresql']['host']
db_port = config['postgresql']['port']
db_name = "Testbase"

# URL for connecting to the main database
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print(DATABASE_URL)
print("==============================================")
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=5,
    max_overflow=10
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def create_database_if_not_exists():
    """Drop and recreate the Testbase database"""
    try:

        
        # Connect to default postgres database first
        conn = await asyncpg.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database='postgres'
        )
        
        # Check if database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )

        if result:
            # Terminate all connections to the database
            await conn.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
            """)
            # Drop the existing database
            await conn.execute(f'DROP DATABASE "{db_name}"')
            print(f"Database '{db_name}' dropped successfully!")
        
        # Create the database
        await conn.execute(f'CREATE DATABASE "{db_name}"')
        print(f"Database '{db_name}' created successfully!")
        
        await conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")


async def create_admins_table_and_seed():
    """Create admins table and add two admin users"""
    async with engine.begin() as conn:
        # Create admins table if not exists
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                age INTEGER NOT NULL
            )
        """))
        print("Admins table created/verified successfully!")
        
        # Check if admins already exist
        result = await conn.execute(text("SELECT COUNT(*) FROM admins"))
        count = result.scalar()
        
        if count == 0:
            # Insert two admin users
            await conn.execute(text("""
                INSERT INTO admins (name, email, age) VALUES
                ('Dhawala Sanka', 'dhawala@example.com', 30),
                ('Vishwa Shakthi', 'vishwa@example.com', 28)
            """))
            print("Two admin users added successfully!")
        else:
            print(f"Admins table already has {count} records. Skipping seed.")

#Create and initialize the database
async def init_db():

    await create_database_if_not_exists()
    await create_admins_table_and_seed()


############## Test the database connection ###############
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