"""
Router for Saraswati Knowledge Module
"""

from fastapi import APIRouter

# Import the actual routes from the module
try:
    from ...modules.saraswati_knowledge.src.api.routes import router as saraswati_router
except ImportError:
    # Fallback if module structure is different
    saraswati_router = APIRouter()
    
    @saraswati_router.get("/")
    async def saraswati_placeholder():
        return {"message": "Saraswati Knowledge Module - Coming Soon"}

router = saraswati_router
