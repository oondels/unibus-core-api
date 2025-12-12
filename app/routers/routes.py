from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Route
from app.schemas import RouteCreate, RouteUpdate, RouteResponse
from app.services import enrich_route_with_geo_data

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
            detail=f"Route with id {route_id} not found",
        )
    return route


@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    """Cria uma nova rota e enriquece com dados da geo-api"""
    # Pega informações geográficas via API externa
    geo_data = await enrich_route_with_geo_data(
        route.origin_city, route.destination_city
    )

    # Cria rota com dados geográficos
    db_route = Route(
        name=route.name,
        origin_city=route.origin_city,
        destination_city=route.destination_city,
        distance_km=geo_data["distance_km"],
        estimated_duration_min=geo_data["estimated_duration_min"],
    )

    db.add(db_route)
    db.commit()
    db.refresh(db_route)

    # Retorna 202 se a geo-api estiver indisponível (dados parciais)
    if not geo_data["geo_api_available"]:
        return HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Route created but geo-api unavailable. Distance and duration not set.",
        )

    return db_route


@router.put("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: int, route: RouteUpdate, db: Session = Depends(get_db)
):
    """Atualiza uma rota e atualiza os dados da geo-api"""
    db_route = db.query(Route).filter(Route.id == route_id).first()
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with id {route_id} not found",
        )

    # Atualiza campos básicos
    db_route.name = route.name
    db_route.origin_city = route.origin_city
    db_route.destination_city = route.destination_city

    # Rebusca dados geográficos se as cidades foram alteradas
    geo_data = await enrich_route_with_geo_data(
        route.origin_city, route.destination_city
    )
    db_route.distance_km = geo_data["distance_km"]
    db_route.estimated_duration_min = geo_data["estimated_duration_min"]

    db.commit()
    db.refresh(db_route)

    if not geo_data["geo_api_available"]:
        return HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Route updated but geo-api unavailable. Distance and duration not refreshed.",
        )

    return db_route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    """Deleta uma rota"""
    db_route = db.query(Route).filter(Route.id == route_id).first()
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with id {route_id} not found",
        )

    db.delete(db_route)
    db.commit()
    return None
