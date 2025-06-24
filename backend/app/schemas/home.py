from datetime import datetime

from pydantic import BaseModel

from .address import AddressCreate, AddressRead
from .user import UserRead


class HomeBase(BaseModel):
    name: str


class HomeCreate(HomeBase):
    address: AddressCreate


class HomeRead(HomeBase):
    id: int
    address: AddressRead
    created_at: datetime
    updated_at: datetime
    creator: UserRead

    class Config:
        orm_mode = True
