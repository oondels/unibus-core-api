from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr


class StudentCreate(StudentBase):
    cep: str = Field(..., min_length=8, max_length=9, pattern=r'^\d{5}-?\d{3}$')


class StudentUpdate(StudentBase):
    cep: str = Field(..., min_length=8, max_length=9, pattern=r'^\d{5}-?\d{3}$')


class StudentResponse(StudentBase):
    id: int
    cep: str
    city: str
    city_ibge_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RouteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    origin_city: str = Field(..., min_length=1, max_length=100)
    destination_city: str = Field(..., min_length=1, max_length=100)


class RouteCreate(RouteBase):
    pass


class RouteUpdate(RouteBase):
    pass


class RouteResponse(RouteBase):
    id: int
    distance_km: Optional[float] = None
    estimated_duration_min: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TripBase(BaseModel):
    route_id: int
    bus_plate: Optional[str] = Field(None, max_length=20)
    departure_time: datetime
    available_seats: int = Field(..., ge=0)


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    bus_plate: Optional[str] = Field(None, max_length=20)
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    available_seats: Optional[int] = Field(None, ge=0)


class TripResponse(TripBase):
    id: int
    arrival_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TripWithRouteResponse(TripResponse):
    route: RouteResponse

    model_config = ConfigDict(from_attributes=True)
