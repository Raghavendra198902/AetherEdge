"""
Router for Kali Security Module
"""

from fastapi import APIRouter

# Import the actual routes from the module
try:
    from ...modules.kali_security.src.api.routes import (
        router as kali_router
    )
except ImportError:
    # Fallback if module structure is different
    kali_router = APIRouter()
    
    @kali_router.get("/")
    async def kali_placeholder():
        return {"message": "Kali Security Module - Coming Soon"}

router = kali_router
