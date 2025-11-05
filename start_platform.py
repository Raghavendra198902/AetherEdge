#!/usr/bin/env python3
"""
🚀 AetherEdge Platform Launcher
===============================
Starts all divine modules and services for development
"""

import subprocess
import time
import sys
import os
import threading
from pathlib import Path

def start_service(name, command, cwd=None):
    """Start a service in a separate process"""
    print(f"🚀 Starting {name}...")
    try:
        if cwd:
            process = subprocess.Popen(
                command, 
                shell=True, 
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            process = subprocess.Popen(
                command, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        print(f"✅ {name} started successfully (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    """Launch all AetherEdge services"""
    print("🌟 AetherEdge Divine Platform Launcher")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    services = []
    
    # 1. Start API Gateway with FastAPI
    print("\n🌐 Starting API Gateway...")
    api_cmd = "uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
    api_process = start_service("API Gateway", api_cmd, base_dir / "api-gateway")
    if api_process:
        services.append(("API Gateway", api_process))
    
    # Wait for API Gateway to start
    time.sleep(3)
    
    # 2. Frontend is already running on port 3000
    print("\n🎨 Frontend is running on http://localhost:3000")
    
    # 3. Start PostgreSQL if not running
    print("\n🗄️ Database services...")
    print("Note: Ensure PostgreSQL is running on localhost:5432")
    
    # 4. Start monitoring services (simplified)
    print("\n📊 Monitoring services...")
    print("Note: Monitoring stack available via Docker Compose when ready")
    
    print("\n" + "=" * 50)
    print("🎉 AetherEdge Platform Services Status:")
    print("=" * 50)
    print("🌐 API Gateway: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🎨 Frontend: http://localhost:3000")
    print("💓 Health Check: http://localhost:8000/health")
    print("\n🔧 Divine Modules Endpoints:")
    print("🧠 Saraswati (Knowledge): http://localhost:8000/api/v1/saraswati")
    print("💰 Lakshmi (FinOps): http://localhost:8000/api/v1/lakshmi")
    print("🛡️ Kali (Security): http://localhost:8000/api/v1/kali")
    print("🐒 Hanuman (Agents): http://localhost:8000/api/v1/hanuman")
    print("🔍 Ganesha (RCA): http://localhost:8000/api/v1/ganesha")
    print("🏗️ Brahma (Blueprint): http://localhost:8000/api/v1/brahma")
    print("⚡ Vishnu (Orchestrator): http://localhost:8000/api/v1/vishnu")
    print("🔄 Shiva (Healer): http://localhost:8000/api/v1/shiva")
    
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop all services")
    
    try:
        # Monitor services
        while True:
            time.sleep(1)
            # Check if any service has stopped
            for name, process in services:
                if process.poll() is not None:
                    print(f"⚠️ {name} has stopped")
                    
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for name, process in services:
            print(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
