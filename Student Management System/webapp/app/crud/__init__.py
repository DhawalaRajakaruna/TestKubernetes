from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.database import engine
from app.models.subject import Subject
from app.models.admin import Admin
import os

async def initialize_default_data():
    async with AsyncSession(engine) as session:
        print("=======================================================")
        try:
            await session.execute(delete(Subject))
            await session.execute(delete(Admin))
            await session.commit()


            subjects = [
                Subject(sub_id=100, name="Physics", description="Into the fundamentals of matter and energy."),
                Subject(sub_id=101, name="Mathematics", description="Heart of all sciences, exploring numbers, shapes, and patterns."),
                Subject(sub_id=102, name="Chemistry", description="Chemistry unravels the secrets of substances and their transformations."),
                Subject(sub_id=103, name="Biology", description="Hunter of life, from cells to ecosystems."),
                Subject(sub_id=104, name="Art", description="Art is the soul's expression, painting emotions and stories on the canvas of life."),
            ]
            session.add_all(subjects)
            await session.flush()

            # Debug: Print all admin environment variables
            print("=== Checking Admin Environment Variables ===")
            admin_env_vars = [
                "ADMIN1_ID", "ADMIN1_USERNAME", "ADMIN1_PASSWORD", "ADMIN1_NAME", "ADMIN1_EMAIL",
                "ADMIN2_ID", "ADMIN2_USERNAME", "ADMIN2_PASSWORD", "ADMIN2_NAME", "ADMIN2_EMAIL"
            ]
            missing_vars = []
            for var in admin_env_vars:
                value = os.getenv(var)
                if value is None:
                    missing_vars.append(var)
                    print(f"  {var}: NOT SET (None)")
                else:
                    # Mask password values
                    if "PASSWORD" in var:
                        print(f"  {var}: ******* (set)")
                    else:
                        print(f"  {var}: {value}")
            
            if missing_vars:
                print(f"ERROR: Missing environment variables: {missing_vars}")
                raise ValueError(f"Missing required environment variables: {missing_vars}")

            # Create admins from environment variables
            admins = [
                Admin(
                    admin_id=int(os.getenv("ADMIN1_ID")),
                    username=os.getenv("ADMIN1_USERNAME"),
                    password=os.getenv("ADMIN1_PASSWORD"),
                    name=os.getenv("ADMIN1_NAME"),
                    email=os.getenv("ADMIN1_EMAIL")
                ),
                Admin(
                    admin_id=int(os.getenv("ADMIN2_ID")),
                    username=os.getenv("ADMIN2_USERNAME"),
                    password=os.getenv("ADMIN2_PASSWORD"),
                    name=os.getenv("ADMIN2_NAME"),
                    email=os.getenv("ADMIN2_EMAIL")
                )
            ]
            
            print(f"Creating Admin 1: ID={os.getenv('ADMIN1_ID')}, Username={os.getenv('ADMIN1_USERNAME')}, Name={os.getenv('ADMIN1_NAME')}, Email={os.getenv('ADMIN1_EMAIL')}")
            print(f"Creating Admin 2: ID={os.getenv('ADMIN2_ID')}, Username={os.getenv('ADMIN2_USERNAME')}, Name={os.getenv('ADMIN2_NAME')}, Email={os.getenv('ADMIN2_EMAIL')}")
            
            session.add_all(admins)
            await session.flush()

            await session.commit()
            print("Default data initialized successfully.")
            print("=======================================================")

        except Exception as e:
            print(f"Error initializing default data: {e}")
            await session.rollback()
