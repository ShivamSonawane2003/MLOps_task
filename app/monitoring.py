import time
from app.logging_utils import setup_logger

logger = setup_logger(__name__)


class MetricsStore:
    """Singleton to store metrics across requests."""
    _instance = None
    _request_count = 0
    _total_latency = 0.0
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsStore, cls).__new__(cls)
        return cls._instance
    
    def increment_request(self, latency):
        """Increment request count and add latency."""
        self._request_count += 1
        self._total_latency += latency
        return self._request_count, self._total_latency
    
    def get_stats(self):
        """Get current statistics."""
        return self._request_count, self._total_latency
    
    def reset(self):
        """Reset all metrics."""
        self._request_count = 0
        self._total_latency = 0.0


# Create singleton instance
_metrics = MetricsStore()


class RequestTimer:
    """Context manager for measuring request latency."""
    
    def __init__(self, operation_name="request"):
        self.operation_name = operation_name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"[TIMER] Started: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        
        if exc_type is not None:
            logger.error(f"[TIMER] Failed: {self.operation_name} - Exception: {exc_type.__name__}")
        else:
            logger.info(f"[TIMER] Completed: {self.operation_name} - {self.elapsed:.3f}s")
        
        return False


def record_request(latency_seconds, session_id=None, route_taken=None, message_preview=None):
    """Log a completed request and update metrics."""
    
    # Handle None latency (e.g., when exception occurs before timer completes)
    if latency_seconds is None:
        logger.warning("Attempted to record request with None latency")
        return
    
    # Use singleton to increment and get current count
    request_count, total_latency = _metrics.increment_request(latency_seconds)
    
    avg_latency = total_latency / request_count
    
    logger.info("\n" + "="*70)
    logger.info(f"REQUEST #{request_count} COMPLETED")
    logger.info("="*70)
    
    if session_id:
        logger.info(f"Session ID: {session_id}")
    
    if message_preview:
        logger.info(f"Message: '{message_preview}'")
    
    if route_taken:
        logger.info(f"Route Taken: {route_taken}")
    
    logger.info("-"*70)
    logger.info(f"REQUEST METRICS:")
    logger.info(f"  |- Request Latency: {latency_seconds:.3f}s ({latency_seconds*1000:.0f}ms)")
    logger.info(f"  |- Average Latency: {avg_latency:.3f}s ({avg_latency*1000:.0f}ms)")
    logger.info(f"  |- Total Requests: {request_count}")
    
    # Performance indicator
    if latency_seconds < 1.0:
        perf_indicator = "FAST"
    elif latency_seconds < 3.0:
        perf_indicator = "NORMAL"
    else:
        perf_indicator = "SLOW"
    
    logger.info(f"\nPerformance: {perf_indicator}")
    logger.info("="*70 + "\n")


def get_metrics():
    """Get current metrics."""
    request_count, total_latency = _metrics.get_stats()
    avg_latency = total_latency / request_count if request_count > 0 else 0
    
    logger.info("\n" + "="*50)
    logger.info("METRICS SUMMARY REQUESTED")
    logger.info("="*50)
    logger.info(f"Total Requests: {request_count}")
    logger.info(f"Total Latency: {total_latency:.3f}s")
    logger.info(f"Average Latency: {avg_latency:.3f}s")
    logger.info("="*50 + "\n")
    
    return {
        "request_count": request_count,
        "total_latency": total_latency,
        "average_latency": avg_latency
    }
