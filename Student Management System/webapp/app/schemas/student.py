from pydantic import BaseModel

class StudentCreate(BaseModel): # Use to Add new student (Save )
    name: str   # All fields required
    age: int    # must send all fields   
    grade: str
    email: str
    subjects: list[str]
    admin_id: int 

class EnrolmentRead(BaseModel): # Nested enrolment data
    enrolment_id: int
    subject_id: int
    subject_name: str
    enrolment_date: str | None = None
    admin_id: int

class StudentRead(BaseModel): # Use to read student data
    std_id: int
    name: str
    age: int
    grade: str
    email: str
    enrolments: list[EnrolmentRead] = []

    class Config:
        from_attributes = True  # Updated for Pydantic v2 (was orm_mode)


class StudentUpdate(BaseModel): #Use to update students
    id: int
    name: str | None = None
    age: int | None = None # this measn those fields are optional
    grade: str | None = None# can be eather with balues or not 
    subjects: list[int] 
    admin_id: int 




    
