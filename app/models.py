from sqlalchemy import Column, ForeignKey, Integer, String
from .database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    # employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)    

class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    description = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

class Employees(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    id_number = Column(Integer, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    middlei = Column(String, nullable=False)
    address = Column(String, nullable=False)
    password = Column(String, nullable=False)