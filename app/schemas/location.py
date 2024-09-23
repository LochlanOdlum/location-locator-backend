from datetime import datetime

from pydantic import BaseModel

from .address import AddressCreate, AddressRead
from .user import UserRead


class LocationBase(BaseModel):
    name: str
    summary: str | None = None
    price_estimate_min: int
    price_estimate_max: int

class LocationCreate(LocationBase):
    address: AddressCreate


class LocationRead(LocationBase):
    id: int
    address: AddressRead
    creator: UserRead
    created_at: datetime
    updated_at: datetime


    class Config:
        orm_mode = True
