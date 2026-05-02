import aiohttp
import os


class LogisticsAPIClient:
    """Client for 3rd-party logistics providers."""

    def __init__(self):
        self.base_url = os.getenv("LOGISTICS_API_URL", "")
        self.api_key = os.getenv("LOGISTICS_API_KEY", "")

    async def get_shipping_quote(self, origin: str, destination: str, weight_kg: float) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                f"{self.base_url}/quotes",
                json={"origin": origin, "destination": destination, "weight_kg": weight_kg},
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
