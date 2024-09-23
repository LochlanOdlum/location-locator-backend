from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from ..utils.database import Base
from .mixins import TimestampMixin


class Address(TimestampMixin, Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    locations = relationship("Location", back_populates="address")
    homes = relationship("Home", back_populates="address")
