import time
from .logging_utils import setup_logger

logger = setup_logger(__name__)

request_count = 0
total_latency = 0.0


class RequestTimer:
    """Context manager for measuring request latency."""
    
    def __init__(self, operation_name="request"):
        self.operation_name = operation_name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        return False


def record_request(latency_seconds):
    """Log a completed request and update metrics."""
    global request_count, total_latency
    
    request_count += 1
    total_latency += latency_seconds
    
    avg_latency = total_latency / request_count
    
    logger.info(
        f"Request #{request_count} - "
        f"Latency: {latency_seconds:.3f}s - "
        f"Avg: {avg_latency:.3f}s"
    )


def get_metrics():
    """Get current metrics."""
    avg_latency = total_latency / request_count if request_count > 0 else 0
    
    return {
        "request_count": request_count,
        "total_latency": total_latency,
        "average_latency": avg_latency
    }
