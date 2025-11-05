"""
Router for Hanuman Agents Module
"""

from fastapi import APIRouter

# Import the actual routes from the module
try:
    from ...modules.hanuman_agents.src.api.routes import (
        router as hanuman_router
    )
except ImportError:
    # Fallback if module structure is different
    hanuman_router = APIRouter()
    
    @hanuman_router.get("/")
    async def hanuman_placeholder():
        return {"message": "Hanuman Agents Module - Coming Soon"}

router = hanuman_router
