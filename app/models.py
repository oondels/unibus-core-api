from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    city = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    origin_city = Column(String, nullable=False)
    destination_city = Column(String, nullable=False)
    distance_km = Column(Float, nullable=True) 
    estimated_duration_min = Column(Integer, nullable=True) 

    # Relationship to trips
    trips = relationship("Trip", back_populates="route", cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    bus_plate = Column(String, nullable=True)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=True)
    available_seats = Column(Integer, nullable=False, default=0)

    # Relationship to route
    route = relationship("Route", back_populates="trips")
