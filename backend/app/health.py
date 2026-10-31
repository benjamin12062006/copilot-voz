from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["salud"])


class HealthStatus(BaseModel):
    status: Literal["ok"]


@router.get("/health")
def read_health() -> HealthStatus:
    """Indica que el proceso responde.

    No consulta Turso, Blob ni Clerk: una caída de un proveedor no debe hacer
    que el orquestador reinicie una API que sigue viva.
    """
    return HealthStatus(status="ok")
