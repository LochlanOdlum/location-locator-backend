from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from ..utils.database import Base
from .mixins import TimestampMixin
from .roles import Role


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(Role), nullable=False, default=Role.USER)

    # SQLAlchemy will row when parents are deleted
    locations = relationship(
        "Location", back_populates="creator", cascade="all, delete-orphan"
    )
    homes = relationship("Home", back_populates="creator", cascade="all, delete-orphan")
