from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subject import Subject

async def get_all_subjects(db: AsyncSession):
    result = await db.execute(select(Subject))
    subjects = result.scalars().all()
    return subjects