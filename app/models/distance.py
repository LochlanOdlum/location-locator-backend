from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..utils.database import Base
from .mixins import TimestampMixin


class Distance(TimestampMixin, Base):
    __tablename__ = "distances"

    id = Column(Integer, primary_key=True, index=True)
    source_home_id = Column(Integer, ForeignKey("homes.id"))
    destination_location_id = Column(Integer, ForeignKey("locations.id"))
    walking_distance_minutes = Column(Integer, nullable=False)

    source = relationship("Home", back_populates="distances")
    destination = relationship("Location", back_populates="distances")
