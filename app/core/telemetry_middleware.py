import time
import psutil
import threading
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.telemetry import telemetry_manager


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically track API request telemetry data.
    This includes request timing, status codes, and basic request information.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Start system metrics collection thread
        self.active_requests = 0
        self.active_requests_lock = threading.Lock()
        self.system_metrics_thread = threading.Thread(target=self._collect_system_metrics, daemon=True)
        self.system_metrics_thread.start()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Increment active requests counter
        with self.active_requests_lock:
            self.active_requests += 1
        
        # Capture request start time and information
        start_time = time.time()
        response = None
        request_id = None
        
        try:
            # Generate the full path for telemetry
            endpoint = f"{request.method} {request.url.path}"
            user_agent = request.headers.get("user-agent", "unknown")
            ip_address = request.client.host if request.client else None
            
            # Get request size if content-length header is present
            content_length = request.headers.get("content-length")
            request_size = int(content_length) if content_length else None
            
            # Process the request
            response = await call_next(request)
            
            # Calculate request duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Get response size
            response_size = int(response.headers.get("content-length", 0))
            
            # Record successful request
            request_id = telemetry_manager.record_api_request(
                endpoint=endpoint,
                method=request.method,
                status_code=response.status_code,
                response_time_ms=duration_ms,
                user_agent=user_agent,
                ip_address=ip_address,
                request_size=request_size,
                response_size=response_size
            )
            
            # Store request_id in response headers for correlation
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate request duration for failed requests
            duration_ms = (time.time() - start_time) * 1000
            
            # Record failed request
            error_message = str(e)
            request_id = telemetry_manager.record_api_request(
                endpoint=endpoint if 'endpoint' in locals() else request.url.path,
                method=request.method,
                status_code=500,  # Assume 500 for unhandled exceptions
                response_time_ms=duration_ms,
                user_agent=user_agent if 'user_agent' in locals() else None,
                ip_address=ip_address if 'ip_address' in locals() else None,
                request_size=request_size if 'request_size' in locals() else None,
                response_size=0,
                error=error_message
            )
            
            # Re-raise the exception to let FastAPI handle it
            raise
        finally:
            # Decrement active requests counter
            with self.active_requests_lock:
                self.active_requests -= 1
    
    def _collect_system_metrics(self):
        """Background thread to collect system metrics periodically"""
        while True:
            try:
                # Collect CPU, memory, and disk metrics every minute
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                with self.active_requests_lock:
                    active_requests = self.active_requests
                
                # Record system metrics
                telemetry_manager.record_system_metrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=disk.percent,
                    active_requests=active_requests
                )
                
                # Sleep for 60 seconds before next collection
                time.sleep(60)
            except Exception as e:
                print(f"Error collecting system metrics: {str(e)}")
                time.sleep(60)  # Still sleep on error