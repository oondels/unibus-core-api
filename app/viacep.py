import httpx
from typing import Optional, Dict, Any


class ViaCEPClient:
    """Cliente para integração com ViaCEP API"""

    def __init__(self):
        self.base_url = "https://viacep.com.br/ws"
        self.timeout = 10.0

    async def get_address(self, cep: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações de endereço pelo CEP usando a API ViaCEP.

        Args:
            cep: CEP no formato 12345678 ou 12345-678

        Returns:
            Dict com dados do endereço ou None se falhar
        """
        # Remove hífen do CEP se existir
        clean_cep = cep.replace("-", "")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/{clean_cep}/json/")

                if response.status_code == 200:
                    data = response.json()

                    # ViaCEP retorna {"erro": true} para CEP inválido
                    if data.get("erro"):
                        print(f"ViaCEP: Invalid CEP {cep}")
                        return None

                    return {
                        "cep": data.get("cep"),
                        "city": data.get("localidade"),
                        "city_ibge_code": data.get("ibge"),
                        "state": data.get("uf"),
                        "neighborhood": data.get("bairro"),
                        "street": data.get("logradouro"),
                    }
                else:
                    print(f"ViaCEP returned status {response.status_code}")
                    return None

        except httpx.TimeoutException:
            print(f"ViaCEP timeout for CEP {cep}")
            return None
        except httpx.RequestError as e:
            print(f"ViaCEP request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error calling ViaCEP: {e}")
            return None


# Singleton instance
viacep_client = ViaCEPClient()
