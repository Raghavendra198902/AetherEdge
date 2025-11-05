"""
Router for Lakshmi FinOps Module
"""

from fastapi import APIRouter

# Import the actual routes from the module
try:
    from ...modules.lakshmi_finops.src.api.routes import (
        router as lakshmi_router
    )
except ImportError:
    # Fallback if module structure is different
    lakshmi_router = APIRouter()
    
    @lakshmi_router.get("/")
    async def lakshmi_placeholder():
        return {"message": "Lakshmi FinOps Module - Coming Soon"}

router = lakshmi_router
