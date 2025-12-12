from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Trip, Route
from app.schemas import TripCreate, TripUpdate, TripResponse, TripWithRouteResponse
from app.services import calculate_arrival_time

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/", response_model=List[TripResponse])
def get_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Busca todas as viagens com paginação"""
    trips = db.query(Trip).offset(skip).limit(limit).all()
    return trips


@router.get("/{trip_id}", response_model=TripWithRouteResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """Busca uma viagem pelo ID com detalhes da rota"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found",
        )
    return trip


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    """Cria uma nova viagem"""
    # Valida se a rota existe
    route = db.query(Route).filter(Route.id == trip.route_id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Route with id {trip.route_id} not found",
        )

    # Calcula o horário de chegada com base na duração estimada da rota
    arrival_time = calculate_arrival_time(
        trip.departure_time, route.estimated_duration_min
    )

    db_trip = Trip(
        route_id=trip.route_id,
        bus_plate=trip.bus_plate,
        departure_time=trip.departure_time,
        arrival_time=arrival_time,
        available_seats=trip.available_seats,
    )

    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: int, trip: TripUpdate, db: Session = Depends(get_db)):
    """Atualiza uma viagem"""
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found",
        )

    # Atualiza apenas os campos fornecidos
    update_data = trip.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trip, key, value)

    # Recalcula o horário de chegada se departure_time mudou e arrival_time não foi fornecido explicitamente
    if "departure_time" in update_data and "arrival_time" not in update_data:
        route = db.query(Route).filter(Route.id == db_trip.route_id).first()
        db_trip.arrival_time = calculate_arrival_time(
            db_trip.departure_time, route.estimated_duration_min
        )

    db.commit()
    db.refresh(db_trip)
    return db_trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    """Deleta uma viagem"""
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found",
        )

    db.delete(db_trip)
    db.commit()
    return None
