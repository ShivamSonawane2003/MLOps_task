from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .graph import get_graph, ChatState
from .monitoring import RequestTimer, record_request
from .logging_utils import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="LLM Chatbot Service", version="1.0")


class ChatRequest(BaseModel):
    session_id: str
    message: str


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
        try:
            session_id = request.session_id
            message = request.message
            
            logger.info(f"[{session_id}] Received: {message}")
            
            # Get the compiled graph
            graph = get_graph()
            
            # Prepare initial state
            initial_state: ChatState = {
                "session_id": session_id,
                "message": message,
                "response": "",
                "route": ""
            }
            
            # Run the graph
            result = graph.invoke(initial_state)
            
            response_text = result.get("response", "No response generated")
            
            logger.info(f"[{session_id}] Response: {response_text[:100]}...")
            
            return ChatResponse(
                response=response_text,
                session_id=session_id
            )
        
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
        
        finally:
            # Record metrics
            record_request(timer.elapsed)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
