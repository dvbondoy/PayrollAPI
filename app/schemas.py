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
    password: str
    id_number: int

class Employee(EmployeeBase):
    pass

class EmployeeResponse(BaseModel):
    firstname: str
    lastname: str
    middlei: str

class Attendance(BaseModel):
    employee_id: int
    date: str
    time_in: str
    time_out: str

class Role(BaseModel):
    role: str
    description: str

    # class Config:
    #     orm_mode = True

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