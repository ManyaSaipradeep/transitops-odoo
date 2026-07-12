from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    cargo_weight = Column(Float, nullable=False)
    planned_distance = Column(Float, nullable=False)
    revenue = Column(Float, default=0.0, nullable=False)
    final_odometer = Column(Float, nullable=True)
    fuel_consumed = Column(Float, nullable=True)
    status = Column(String, default="Draft", nullable=False)

    vehicle = relationship("Vehicle")
    driver = relationship("Driver")
