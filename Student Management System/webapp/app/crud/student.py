from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student import Student
from app.models.enrolment import Enrolment
from app.schemas.student import StudentCreate, StudentUpdate
from datetime import date

import app.crud.enrolment as enrolment_crud

from fastapi.responses import HTMLResponse

#Create Student
async def create_student(db: AsyncSession, student_data: StudentCreate):
    try:
        # Check for same emails (uncommented and fixed)
        result = await db.execute(
            select(Student).where(Student.email == student_data.email)
        )
        existing_student = result.scalar_one_or_none() 
        if existing_student:
            return None  # Return None to indicate duplicate email
        
        new_student = Student(
            name=student_data.name,
            age=student_data.age,
            grade=student_data.grade,
            email=student_data.email
        )
        db.add(new_student)
        await db.flush()  
        await enrolment_crud.enrol_student_in_subject(db,student_data.subjects,new_student.std_id,student_data.admin_id)
        await db.commit()
        await db.refresh(new_student)
        print(f"{new_student.name} created with enrollments.")
        return new_student
    except Exception as e:
        await db.rollback()
        raise e

#Get all students
async def get_students(db: AsyncSession):
    # Load students with enrolments AND each enrolment's subject
    result = await db.execute(
        select(Student).options(
            selectinload(Student.enrolments).selectinload(Enrolment.subject)
        )
    )
    students = result.scalars().all()
    
    output = []
    
    for s in students:
        output.append({
            "std_id": s.std_id,
            "name": s.name,
            "age": s.age,
            "grade": s.grade,
            "email": s.email,
            "enrolments": [
                {
                    "enrolment_id": e.enrolment_id,
                    "subject_id": e.subject_id,
                    "subject_name": e.subject.name, 
                    "enrolment_date": e.enrolment_date,
                    "admin_id": e.admin_id,
                }
                for e in s.enrolments
            ]
        })

    #=============================================================
    # Debugging output
    # Handle the load that a single list carry 
    # Important
    #=============================================================

    return output

async def get_student_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(Student)
        .where(Student.email == email)
        .options(
            selectinload(Student.enrolments).selectinload(Enrolment.subject)
        )
    )
    student = result.scalars().first()
    
    if not student:
        return None
    
    # Return formatted output with enrolments
    return {
        "std_id": student.std_id,
        "name": student.name,
        "age": student.age,
        "grade": student.grade,
        "email": student.email,
        "enrolments": [
            {
                "enrolment_id": e.enrolment_id,
                "subject_id": e.subject_id,
                "subject_name": e.subject.name,
                "enrolment_date": str(e.enrolment_date) if e.enrolment_date else None,
                "admin_id": e.admin_id,
            }
            for e in student.enrolments
        ]
    }

async def update_student(db: AsyncSession, student_data: StudentUpdate):
    print("Update student called in CRUD")
    try:
        # Load student with enrolments
        result = await db.execute(
            select(Student)
            .where(Student.std_id == student_data.id)
            .options(selectinload(Student.enrolments))
        )
        student = result.scalars().first()

        if not student:
            return None

        #Since None will not pass here
        student.name = student_data.name
        student.age = student_data.age
        student.grade = student_data.grade


        
        await enrolment_crud.update_enrolments(student,student_data.subjects, db,student_data.admin_id)
        print('=======================')
        #print(f"Student fetched for update: {student.id, student.name, student.age, student.grade, student.email}")
        
        await db.commit()
        await db.refresh(student)
        return student
    except Exception as e:
        await db.rollback()
        return {"error": str(e)}, 500


async def delete_student_by_email(db: AsyncSession, email: str):

    try:
        result = await db.execute(select(Student).where(Student.email == email))
        student = result.scalars().first()
        
        await enrolment_crud.delete_enrolments_by_student(db, student.std_id)

        if not student:
            return None 
        
        await db.delete(student)
        await db.commit()
        return student
        
    except Exception as e:
        await db.rollback()
        return {"error": str(e)}, 500
       


