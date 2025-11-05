"""
API Routers for AetherEdge Platform

All module-specific API routers and route definitions.
"""

from .health_router import router as health_router
from .auth_router import router as auth_router
from .brahma_router import router as brahma_router
from .vishnu_router import router as vishnu_router
from .shiva_router import router as shiva_router
from .lakshmi_router import router as lakshmi_router
from .kali_router import router as kali_router

__all__ = [
    "health_router",
    "auth_router",
    "brahma_router",
    "vishnu_router",
    "shiva_router",
    "lakshmi_router",
    "kali_router"
]
