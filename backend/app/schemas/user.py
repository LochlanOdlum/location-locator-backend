from datetime import datetime

from pydantic import BaseModel, EmailStr
from ..models.roles import Role


class UserSignIn(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    role: Role


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
