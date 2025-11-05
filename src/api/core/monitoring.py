"""
Monitoring and metrics configuration

Handles Prometheus metrics, OpenTelemetry tracing, and health monitoring
for the AetherEdge API platform.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
import time
import logging
from typing import Dict, Any
import psutil
import asyncio

from .config import settings

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'aetheredge_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'aetheredge_api_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'aetheredge_api_active_connections',
    'Number of active connections'
)

DATABASE_CONNECTIONS = Gauge(
    'aetheredge_database_connections',
    'Number of database connections',
    ['state']
)

SYSTEM_INFO = Info(
    'aetheredge_system',
    'System information'
)

MODULE_STATUS = Gauge(
    'aetheredge_module_status',
    'Module status (1=healthy, 0=unhealthy)',
    ['module']
)

ERROR_COUNT = Counter(
    'aetheredge_api_errors_total',
    'Total number of API errors',
    ['error_type', 'endpoint']
)

CACHE_OPERATIONS = Counter(
    'aetheredge_cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)


class MetricsCollector:
    """Collect and manage application metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
    def record_request(self, method: str, endpoint: str,
                       status_code: int, duration: float):
        """Record API request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        self.request_count += 1
        
        if status_code >= 400:
            self.error_count += 1
            ERROR_COUNT.labels(
                error_type=f"http_{status_code}",
                endpoint=endpoint
            ).inc()
    
    def record_database_connections(self, total: int, active: int, idle: int):
        """Record database connection metrics"""
        DATABASE_CONNECTIONS.labels(state="total").set(total)
        DATABASE_CONNECTIONS.labels(state="active").set(active)
        DATABASE_CONNECTIONS.labels(state="idle").set(idle)
    
    def record_module_status(self, module: str, healthy: bool):
        """Record module health status"""
        MODULE_STATUS.labels(module=module).set(1 if healthy else 0)
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics"""
        CACHE_OPERATIONS.labels(
            operation=operation,
            result=result
        ).inc()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "uptime_seconds": time.time() - self.start_time,
                "total_requests": self.request_count,
                "total_errors": self.error_count
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}


# Global metrics collector
metrics = MetricsCollector()


def setup_tracing():
    """Setup OpenTelemetry tracing"""
    try:
        if settings.ENVIRONMENT == "production":
            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=settings.JAEGER_AGENT_HOST,
                agent_port=settings.JAEGER_AGENT_PORT,
            )
            
            # Setup trace provider
            trace.set_tracer_provider(TracerProvider())
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            
            logger.info("OpenTelemetry tracing configured")
        else:
            logger.info("Tracing disabled in development mode")
            
    except Exception as e:
        logger.error(f"Error setting up tracing: {str(e)}")


def setup_metrics():
    """Setup monitoring and metrics collection"""
    try:
        # Setup tracing
        setup_tracing()
        
        # Set system information
        SYSTEM_INFO.info({
            'version': settings.VERSION,
            'environment': settings.ENVIRONMENT,
            'python_version': '3.11+',
            'app_name': settings.APP_NAME
        })
        
        # Initialize module status
        modules = ['brahma', 'vishnu', 'shiva', 'lakshmi', 'kali']
        for module in modules:
            MODULE_STATUS.labels(module=module).set(1)
        
        logger.info("Metrics setup complete")
        
    except Exception as e:
        logger.error(f"Error setting up metrics: {str(e)}")


def instrument_app(app):
    """Instrument FastAPI app with OpenTelemetry"""
    try:
        if settings.ENVIRONMENT == "production":
            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(app)
            
            # Instrument SQLAlchemy
            SQLAlchemyInstrumentor().instrument()
            
            # Instrument Redis
            RedisInstrumentor().instrument()
            
            logger.info("Application instrumentation complete")
        else:
            logger.info("Instrumentation disabled in development mode")
            
    except Exception as e:
        logger.error(f"Error instrumenting application: {str(e)}")


async def collect_background_metrics():
    """Background task to collect system metrics"""
    while True:
        try:
            # Collect system metrics
            system_metrics = metrics.get_system_metrics()
            
            # Update Prometheus gauges
            if "cpu_percent" in system_metrics:
                # Note: We'd need to define these gauges first
                pass
            
            # Sleep for 30 seconds
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in background metrics collection: {str(e)}")
            await asyncio.sleep(60)  # Wait longer on error


def get_health_metrics() -> Dict[str, Any]:
    """Get health check metrics"""
    return {
        "metrics": {
            "total_requests": metrics.request_count,
            "total_errors": metrics.error_count,
            "uptime_seconds": time.time() - metrics.start_time,
        },
        "system": metrics.get_system_metrics()
    }
