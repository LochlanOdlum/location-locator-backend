from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..utils.database import Base
from .mixins import TimestampMixin


class Location(TimestampMixin, Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    description = Column(String, nullable=False)
    price_estimate_min = Column(Integer, nullable=False)
    price_estimate_max = Column(Integer, nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    # Explicitly specify cascasde delete in DB to delete location when creation user is deleted
    creation_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    address = relationship("Address", back_populates="locations")
    creator = relationship("User", back_populates="locations")
    distances = relationship(
        "Distance", back_populates="destination", cascade="all, delete-orphan"
    )
