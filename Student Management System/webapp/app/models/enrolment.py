from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Enrolment(Base):  # Bridge table for Many-to-Many relationship
    __tablename__ = "enrolments"

    enrolment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.std_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.sub_id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("admins.admin_id"), nullable=False)
    enrolment_date = Column(String)

    # Relationships
    student = relationship("Student", back_populates="enrolments")
    subject = relationship("Subject", back_populates="enrolments")
    admin = relationship("Admin", back_populates="enrolments")