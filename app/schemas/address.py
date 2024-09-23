from datetime import datetime

from pydantic import BaseModel


class AddressBase(BaseModel):
    street: str
    city: str
    postal_code: str
    country: str


class AddressCreate(AddressBase):
    pass


class AddressRead(AddressBase):
    id: int
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
