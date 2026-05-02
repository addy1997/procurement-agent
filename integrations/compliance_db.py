import aiohttp
import os


class ComplianceDBClient:
    """Client for external compliance and certification databases."""

    def __init__(self):
        self.base_url = os.getenv("COMPLIANCE_DB_URL", "")
        self.api_key = os.getenv("COMPLIANCE_DB_KEY", "")

    async def verify_vendor(self, vendor_id: str) -> dict:
        headers = {"X-API-Key": self.api_key}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(f"{self.base_url}/vendors/{vendor_id}/certifications") as resp:
                resp.raise_for_status()
                return await resp.json()
