from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    sub_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)

    # Relationship to enrolments
    enrolments = relationship("Enrolment", back_populates="subject")