from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from .llm import create_llm_chain
from .calculator import calculate
from .memory import get_or_create_memory, add_to_memory, get_memory_context
from .logging_utils import setup_logger

logger = setup_logger(__name__)


class ChatState(TypedDict):
    """State passed through the graph."""
    session_id: str
    message: str
    response: str
    route: str


def router_node(state: ChatState) -> ChatState:
    """Route to calculator or LLM based on content."""
    message = state["message"].lower()
    
    # Check if it's a math expression
    if any(op in message for op in ['+', '-', '*', '/', '%', '**']):
        if any(char.isdigit() for char in message):
            state["route"] = "calculator"
            logger.info(f"Routing to calculator: {message}")
            return state
    
    state["route"] = "llm"
    logger.info(f"Routing to LLM: {message}")
    return state


def calculator_node(state: ChatState) -> ChatState:
    """Process math expressions."""
    result = calculate(state["message"])
    if result:
        state["response"] = result
        logger.info(f"Calculator result: {result}")
    else:
        state["response"] = "I couldn't calculate that expression."
    
    return state


def llm_node(state: ChatState) -> ChatState:
    """Generate response using LLM with memory."""
    session_id = state["session_id"]
    user_message = state["message"]
    
    memory = get_or_create_memory(session_id)
    memory_context = get_memory_context(session_id)
    
    # Build input with memory context
    input_text = user_message
    if memory_context:
        input_text = f"Previous context:\n{memory_context}\n\nNew message: {user_message}"
    
    chain = create_llm_chain()
    response = chain.invoke({"input": input_text})
    
    # Extract text from response
    if hasattr(response, 'content'):
        response_text = response.content
    else:
        response_text = str(response)
    
    # Save to memory
    add_to_memory(session_id, user_message, response_text)
    
    state["response"] = response_text
    logger.info(f"LLM response for {session_id}: {response_text[:100]}...")
    
    return state


def build_graph():
    """Build the LangGraph DAG."""
    graph = StateGraph(ChatState)
    
    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("calculator", calculator_node)
    graph.add_node("llm", llm_node)
    
    # Set start node
    graph.set_entry_point("router")
    
    # Conditional routing based on router decision
    def route_decision(state):
        if state["route"] == "calculator":
            return "calculator"
        else:
            return "llm"
    
    # Add conditional edges
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "calculator": "calculator",
            "llm": "llm"
        }
    )
    
    # Add final edges to end (no need to add end node explicitly)
    graph.add_edge("calculator", "__end__")
    graph.add_edge("llm", "__end__")
    
    # Compile
    app = graph.compile()
    logger.info("LangGraph compiled successfully")
    
    return app


# Global graph instance
_graph_instance = None


def get_graph():
    """Get or create the compiled graph."""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = build_graph()
    return _graph_instance
