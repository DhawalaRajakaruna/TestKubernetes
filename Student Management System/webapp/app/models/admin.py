from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to enrolments
    enrolments = relationship("Enrolment", back_populates="admin")
