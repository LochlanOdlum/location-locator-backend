from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserSignIn(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
