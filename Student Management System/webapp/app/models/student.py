from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    std_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    age = Column(Integer)
    grade = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to enrolments
    enrolments = relationship("Enrolment", back_populates="student")