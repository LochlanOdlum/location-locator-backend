from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..utils.database import Base
from .mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    locations = relationship("Location", back_populates="creator")
    homes = relationship("Home", back_populates="creator")

