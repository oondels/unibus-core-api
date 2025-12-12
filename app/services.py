from datetime import datetime, timedelta
from typing import Optional
from app.external import geo_client


async def enrich_route_with_geo_data(
    origin_city: str, destination_city: str
) -> dict:
    """
    Chama a geo-api para obter distância e duração de uma rota.

    Retorna:
        Dicionário com 'distance_km', 'estimated_duration_min' e a flag 'geo_api_available'
    """
    geo_data = await geo_client.get_distance_and_duration(origin_city, destination_city)

    if geo_data:
        return {
            "distance_km": geo_data.get("distance_km"),
            "estimated_duration_min": geo_data.get("estimated_duration_min"),
            "geo_api_available": True,
        }
    else:
        return {
            "distance_km": None,
            "estimated_duration_min": None,
            "geo_api_available": False,
        }


def calculate_arrival_time(
    departure_time: datetime, estimated_duration_min: Optional[int]
) -> Optional[datetime]:
    """
    Calcula o horário de chegada com base no horário de partida e na duração estimada.

    Parâmetros:
        departure_time: datetime agendado de partida
        estimated_duration_min: duração estimada em minutos (pode ser None)

    Retorna:
        datetime calculado de chegada ou None se a duração não estiver disponível
    """
    if estimated_duration_min is not None and estimated_duration_min > 0:
        return departure_time + timedelta(minutes=estimated_duration_min)
    return None
