import aiohttp
import os


class SupplierAPIClient:
    """Async HTTP client for querying external supplier APIs."""

    def __init__(self):
        self.base_url = os.getenv("SUPPLIER_API_URL", "")
        self.api_key = os.getenv("SUPPLIER_API_KEY", "")

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                f"{self.base_url}/search",
                params={"q": query, "limit": limit},
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("results", [])
