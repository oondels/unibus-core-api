import httpx
import os
from typing import Optional, Dict, Any


class GeoAPIClient:
    """Client for interacting with unibus-geo-api"""

    def __init__(self):
        self.base_url = os.getenv("GEO_API_URL", "http://localhost:8001")
        self.timeout = float(os.getenv("GEO_API_TIMEOUT", "10.0"))

    async def get_distance_and_duration(
        self, origin: str, destination: str
    ) -> Optional[Dict[str, Any]]:
        """
        Chama a geo-api para obter a distância e a duração estimada entre duas cidades.

        Args:
            origin: nome da cidade de origem
            destination: nome da cidade de destino

        Returns:
            Dicionário com 'distance_km' e 'estimated_duration_min' ou None em caso de falha
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/distance",
                    json={"origin": origin, "destination": destination},
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "distance_km": data.get("distance_km"),
                        "estimated_duration_min": data.get("estimated_duration_min"),
                    }
                else:
                    print(
                        f"Geo-API returned status {response.status_code}: {response.text}"
                    )
                    return None

        except httpx.TimeoutException:
            print(f"Geo-API timeout after {self.timeout}s")
            return None
        except httpx.RequestError as e:
            print(f"Geo-API request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error calling Geo-API: {e}")
            return None


geo_client = GeoAPIClient()
