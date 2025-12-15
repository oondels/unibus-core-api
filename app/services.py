from datetime import datetime, timedelta
from typing import Optional
from app.external import validation_client
from app.viacep import viacep_client


async def validate_cep(cep: str) -> dict:
    """
    Valida CEP e busca informações de cidade usando ViaCEP.

    Args:
        cep: CEP no formato 12345678 ou 12345-678

    Returns:
        Dicionário com 'is_valid', 'city', 'city_ibge_code' e 'reason'
    """
    address_data = await viacep_client.get_address(cep)

    if address_data and address_data.get("city") and address_data.get("city_ibge_code"):
        return {
            "is_valid": True,
            "city": address_data["city"],
            "city_ibge_code": address_data["city_ibge_code"],
            "state": address_data.get("state"),
            "reason": "CEP valid",
        }
    else:
        return {
            "is_valid": False,
            "city": None,
            "city_ibge_code": None,
            "state": None,
            "reason": "Invalid CEP",
        }


async def validate_student_eligibility(
    name: str, email: str, registration: str
) -> dict:
    """
    Chama a validation-api para validar elegibilidade do estudante.

    Retorna:
        Dicionário com 'is_valid', 'reason' e 'validation_api_available'
    """
    validation_data = await validation_client.validate_student(name, email, registration)

    if validation_data:
        return {
            "is_valid": validation_data.get("is_valid", False),
            "reason": validation_data.get("reason", "Unknown"),
            "validation_api_available": True,
        }
    else:
        # Se a API de validação está indisponível, aceita o estudante por padrão
        return {
            "is_valid": True,
            "reason": "Validation API unavailable - student accepted by default",
            "validation_api_available": False,
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
