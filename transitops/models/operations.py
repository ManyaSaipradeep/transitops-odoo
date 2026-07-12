from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
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

class FuelLog(Base):
    __tablename__ = "fuel_logs"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    liters = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
