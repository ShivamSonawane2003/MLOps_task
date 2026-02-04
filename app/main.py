from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from app.graph import get_graph, ChatState
from app.monitoring import RequestTimer, record_request
from app.logging_utils import setup_logger
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = setup_logger(__name__)

app = FastAPI(title="LLM Chatbot Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shivamsonawane2003.github.io"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ChatRequest(BaseModel):
    session_id: str
    message: str
    prompt_variant: str = "professional"  # Default to professional


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.on_event("startup")
def startup_event():
    """Initialize graph on startup."""
    logger.info("Server starting up")
    get_graph()
    logger.info("Graph initialized")


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint.
    
    Args:
        request: ChatRequest with session_id and message
    
    Returns:
        ChatResponse with AI response
    """
    
    with RequestTimer() as timer:
        session_id = request.session_id
        message = request.message
        prompt_variant = request.prompt_variant
        route_taken = "unknown"
        response_text = ""
        
        try:
            logger.info(f"[{session_id}] === NEW REQUEST === Message: '{message}' | Variant: {prompt_variant}")
            
            # Get the compiled graph
            graph = get_graph()
            
            # Prepare initial state
            initial_state: ChatState = {
                "session_id": session_id,
                "message": message,
                "response": "",
                "route": "",
                "prompt_variant": prompt_variant
            }
            
            # Run the graph
            result = graph.invoke(initial_state)
            
            response_text = result.get("response", "No response generated")
            route_taken = result.get("route", "unknown")
            
            logger.info(f"[{session_id}] === RESPONSE COMPLETE === Route: {route_taken.upper()} | Response: {response_text[:100]}...")
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            route_taken = "ERROR"
            raise HTTPException(status_code=500, detail=str(e))
    
    # Record metrics after timer context exits
    record_request(
        latency_seconds=timer.elapsed,
        session_id=session_id,
        route_taken=route_taken.upper(),
        message_preview=message[:100] if len(message) > 100 else message
    )
    
    return ChatResponse(
        response=response_text,
        session_id=session_id
    )


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/metrics")
def get_metrics_endpoint():
    """Get current monitoring metrics."""
    from app.monitoring import get_metrics
    metrics = get_metrics()
    return metrics


@app.get("/test_ui", response_class=HTMLResponse)
def test_ui():
    """Serve test UI from static/index.html."""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        return FileResponse(html_file, media_type="text/html")
    return "<h1>Test UI not found</h1>"


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8001)
