import aiohttp
import os


class ERPConnector:
    """Async HTTP client for internal DB / ERP system integration."""

    def __init__(self):
        self.endpoints = [ep.strip() for ep in os.getenv("ERP_ENDPOINTS", "").split(",") if ep.strip()]

    async def get_stock_levels(self, product_id: str) -> list[dict]:
        results = []
        async with aiohttp.ClientSession() as session:
            for endpoint in self.endpoints:
                async with session.get(f"{endpoint}/stock/{product_id}") as resp:
                    if resp.status == 200:
                        results.append(await resp.json())
        return results

    async def update_stock(self, product_id: str, quantity: int) -> bool:
        async with aiohttp.ClientSession() as session:
            for endpoint in self.endpoints:
                async with session.post(
                    f"{endpoint}/stock/{product_id}",
                    json={"quantity": quantity},
                ) as resp:
                    if resp.status not in (200, 204):
                        return False
        return True
