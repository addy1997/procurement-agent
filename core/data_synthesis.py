import json
from datetime import datetime
from typing import Any

import numpy as np
from pydantic import BaseModel, Field


class SupplierScore(BaseModel):
    name: str
    reliability_score: float = Field(ge=0.0, le=5.0)
    compliance_passed: bool
    composite_score: float = Field(ge=0.0, le=1.0)


class DataSynthesizer:
    """Normalizes and ranks supplier data using NumPy and Pydantic models."""

    @staticmethod
    def rank_suppliers(suppliers: list[dict]) -> list[SupplierScore]:
        if not suppliers:
            return []

        scores = np.array([s.get("reliability_score", 0.0) for s in suppliers], dtype=float)
        normalized = scores / 5.0

        ranked = []
        for supplier, composite in zip(suppliers, normalized):
            ranked.append(SupplierScore(
                name=supplier.get("name", "Unknown"),
                reliability_score=supplier.get("reliability_score", 0.0),
                compliance_passed=supplier.get("compliance_passed", False),
                composite_score=round(float(composite), 4),
            ))

        ranked.sort(key=lambda s: s.composite_score, reverse=True)
        return ranked

    @staticmethod
    def to_json(data: Any) -> str:
        def handler(obj):
            return obj.isoformat() if isinstance(obj, datetime) else str(obj)
        return json.dumps(data, default=handler)
