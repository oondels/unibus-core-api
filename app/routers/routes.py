from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Route
from app.schemas import RouteCreate, RouteUpdate, RouteResponse

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/", response_model=List[RouteResponse])
def get_routes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Coleta todas as rotas com paginação"""
    routes = db.query(Route).offset(skip).limit(limit).all()
    return routes


@router.get("/{route_id}", response_model=RouteResponse)
def get_route(route_id: int, db: Session = Depends(get_db)):
    """Coleta uma rota pelo ID"""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rota com ID {route_id} não encontrada",
        )
    return route


@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    """Cria uma nova rota"""
    db_route = Route(
        name=route.name,
        origin_city=route.origin_city,
        destination_city=route.destination_city,
        distance_km=None,
        estimated_duration_min=None,
    )

    db.add(db_route)
    db.commit()
    db.refresh(db_route)

    return db_route


@router.put("/{route_id}", response_model=RouteResponse)
def update_route(
    route_id: int, route: RouteUpdate, db: Session = Depends(get_db)
):
    """Atualiza uma rota"""
    db_route = db.query(Route).filter(Route.id == route_id).first()
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rota com ID {route_id} não encontrada",
        )

    # Atualiza campos básicos
    db_route.name = route.name
    db_route.origin_city = route.origin_city
    db_route.destination_city = route.destination_city

    db.commit()
    db.refresh(db_route)

    return db_route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    """Deleta uma rota"""
    db_route = db.query(Route).filter(Route.id == route_id).first()
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rota com ID {route_id} não encontrada",
        )

    db.delete(db_route)
    db.commit()
    return None
