from typing import Optional
from pydantic import BaseModel

# pydantic BaseModel is a special class that allows us to define the request body and the response body of our API
# BaseModel is a special class that comes from Pydantic. It allows us to define the request body and the response body of our API.
# Schema
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

class EmployeeBase(BaseModel):
    firstname: str
    lastname: str
    middlei: str
    address: str
    id_number: int
    password: str
    gender: str
    birthday: str
    phone_number: str
    employment_status: str
    position: str
    supervisor_id: str
    basic_salary: float
    gsm_rate: float
    hourly_rate: float

class Employee(EmployeeBase):
    pass

class EmployeeResponse(BaseModel):
    firstname: str
    lastname: str
    middlei: str

class Attendance(BaseModel):
    employee_id: int
    start_date: str
    end_date: str
    total_hours: float
    notes: str

class Role(BaseModel):
    role: str
    description: str

class RoleResponse(BaseModel):
    role: str
    description: str
    employee_id: int

    class Config:
        orm_mode = True

class RoleOut(BaseModel):
    role: str
    description: str
    employee_id: int
    count: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None