from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..utils.database import Base
from .mixins import TimestampMixin


class Home(TimestampMixin, Base):
    __tablename__ = "homes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    creation_user_id = Column(Integer, ForeignKey("users.id"))

    address = relationship("Address", back_populates="homes")
    creator = relationship("User", back_populates="homes")
    distances = relationship("Distance", back_populates="source", cascade="all, delete-orphan")
