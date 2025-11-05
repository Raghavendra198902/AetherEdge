#!/usr/bin/env python3
"""
🚀 AetherEdge API Gateway Startup Script
========================================
Properly starts the API Gateway with correct module paths
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "api-gateway"))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the AetherEdge API Gateway"""
    try:
        logger.info("🚀 Starting AetherEdge Divine API Gateway...")
        logger.info(f"Project root: {project_root}")
        logger.info(f"Python path: {sys.path[:3]}")
        
        # Change to API Gateway directory
        os.chdir(project_root / "api-gateway")
        
        # Import and run the server
        from src.main import app
        import uvicorn
        
        logger.info("✅ API Gateway initialized successfully")
        logger.info("🌐 Starting server on http://localhost:8000")
        logger.info("📚 API Documentation: http://localhost:8000/docs")
        logger.info("🔍 Health Check: http://localhost:8000/health")
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start API Gateway: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
