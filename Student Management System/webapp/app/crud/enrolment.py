from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrolment import Enrolment
from app.models.student import Student


async def delete_enrolments_by_student(db: AsyncSession, std_id: int):
    try:
        result = await db.execute(
            select(Enrolment).where(Enrolment.student_id == std_id)
        )
        enrolments = result.scalars().all()
        
        for enrolment in enrolments:
            await db.delete(enrolment)
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Error deleting enrolments for student {std_id}: {e}")

async def enrol_student_in_subject(db: AsyncSession, sub_ids: list, std_id: int, admin_id: int):
    for sub_id in sub_ids:
        new_enrollment = Enrolment(
            student_id=std_id,
            subject_id=int(sub_id),
            admin_id=admin_id,
            enrolment_date="None"  # Set default value (can be updated later
        )
        db.add(new_enrollment)
        print('Done enrolling.....')

async def update_enrolments(student : Student, new_sub_ids : list, db: AsyncSession,admin_id:int):
    current_enrolment_ids = [e.subject_id for e in student.enrolments]
    print(f"Current enrolment IDs: {current_enrolment_ids}")
    print(f'New submitted IDs    : {new_sub_ids}')
    
    #new enrolment
    new_enrol_sub_ids = list( # {100,102}-{100,101} = {102}
        set(new_sub_ids) - set(current_enrolment_ids)
    )
    print("Have to enrol this : ",new_enrol_sub_ids)
    #enrol_student_in_subject(db,new_enrol_sub_ids, student.std_id, admin_id)
    if new_enrol_sub_ids:
            for sub_id in new_enrol_sub_ids:
                new_enrollment = Enrolment(
                    student_id=student.std_id,
                    subject_id=sub_id,
                    admin_id=admin_id,  
                    enrolment_date="None"  # Set default value (can be updated later)
                )
                db.add(new_enrollment)
    #removing enrolment
    for enrolment in student.enrolments:
        if enrolment.subject_id not in new_sub_ids:
            await db.delete(enrolment)  
            print('Record Deleted .......')

    pass