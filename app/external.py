import httpx
import os
from typing import Optional, Dict, Any


class StudentValidationClient:
    """Cliente para integração com unibus-student-validation-api"""

    def __init__(self):
        self.base_url = os.getenv("VALIDATION_API_URL", "http://localhost:8001")
        self.timeout = float(os.getenv("VALIDATION_API_TIMEOUT", "10.0"))

    async def validate_student(
        self, name: str, email: str, registration: str
    ) -> Optional[Dict[str, Any]]:
        """
        Chama a validation-api para validar elegibilidade do estudante.

        Args:
            name: Nome do estudante
            email: Email do estudante
            registration: Matrícula do estudante

        Returns:
            Dict com 'is_valid' e 'reason' ou None se falhar
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/validate-student",
                    json={
                        "name": name,
                        "email": email,
                        "registration": registration
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "is_valid": data.get("is_valid", False),
                        "reason": data.get("reason", "Unknown"),
                    }
                else:
                    print(
                        f"Validation-API returned status {response.status_code}: {response.text}"
                    )
                    return None

        except httpx.TimeoutException:
            print(f"Validation-API timeout after {self.timeout}s")
            return None
        except httpx.RequestError as e:
            print(f"Validation-API request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error calling Validation-API: {e}")
            return None


validation_client = StudentValidationClient()
