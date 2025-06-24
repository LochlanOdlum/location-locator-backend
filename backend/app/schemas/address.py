from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AddressBase(BaseModel):
    street: str
    city: str
    postal_code: str
    country: str


class AddressCreate(AddressBase):
    latitude: Optional[float]
    longitude: Optional[float]


class AddressRead(AddressBase):
    id: int
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
