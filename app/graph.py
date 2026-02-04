from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from app.llm import create_llm_chain
from app.calculator import calculate
from app.memory import get_or_create_memory, add_to_memory, get_memory_context
from app.logging_utils import setup_logger

logger = setup_logger(__name__)


class ChatState(TypedDict):
    """State passed through the graph."""
    session_id: str
    message: str
    response: str
    route: str
    prompt_variant: str  # Added for prompt variant selection


def router_node(state: ChatState) -> ChatState:
    """Route to calculator or LLM based on content."""
    message = state["message"].lower()
    session_id = state["session_id"]
    
    # Check if it's a math expression
    if any(op in message for op in ['+', '-', '*', '/', '%', '**']):
        if any(char.isdigit() for char in message):
            state["route"] = "calculator"
            logger.info(f"[{session_id}] ROUTER DECISION: Calculator Node | Input: '{state['message']}'")
            return state
    
    state["route"] = "llm"
    logger.info(f"[{session_id}] ROUTER DECISION: LLM Node | Input: '{state['message']}'")
    return state


def calculator_node(state: ChatState) -> ChatState:
    """Process math expressions."""
    session_id = state["session_id"]
    message = state["message"]
    
    logger.info(f"[{session_id}] CALCULATOR NODE PROCESSING: '{message}'")
    
    result = calculate(message)
    if result:
        state["response"] = result
        logger.info(f"[{session_id}] CALCULATOR NODE OUTPUT: {result}")
    else:
        state["response"] = "I couldn't calculate that expression."
        logger.info(f"[{session_id}] CALCULATOR NODE: Could not process expression")
    
    return state


def llm_node(state: ChatState) -> ChatState:
    """Generate response using LLM with memory."""
    session_id = state["session_id"]
    user_message = state["message"]
    prompt_variant = state.get("prompt_variant", "professional")  # Default to professional
    
    logger.info(f"[{session_id}] LLM NODE PROCESSING: '{user_message}' | Prompt Variant: {prompt_variant}")
    
    memory = get_or_create_memory(session_id)
    memory_context = get_memory_context(session_id)
    
    if memory_context:
        logger.info(f"[{session_id}] LLM NODE: Using conversation history (memory active)")
    
    # Build input with memory context
    input_text = user_message
    if memory_context:
        input_text = f"Previous context:\n{memory_context}\n\nNew message: {user_message}"
    
    # Create chain with selected prompt variant
    from app.llm import get_llm, get_prompt_template
    llm = get_llm()
    prompt = get_prompt_template(prompt_variant)
    
    # Create the chain
    class PromptLLMChain:
        def __init__(self, prompt_template, llm_model):
            self.prompt_template = prompt_template
            self.llm_model = llm_model
        
        def invoke(self, inputs):
            formatted_prompt = self.prompt_template.format(**inputs)
            response = self.llm_model.invoke({"input": formatted_prompt})
            return response
    
    chain = PromptLLMChain(prompt, llm)
    
    logger.info(f"[{session_id}] LLM NODE: Calling Google Gemini API...")
    response = chain.invoke({"input": input_text})
    
    # Extract text from response
    if hasattr(response, 'content'):
        response_text = response.content
    else:
        response_text = str(response)
    
    logger.info(f"[{session_id}] LLM NODE OUTPUT: {response_text[:150]}...")
    
    # Save to memory
    add_to_memory(session_id, user_message, response_text)
    logger.info(f"[{session_id}] LLM NODE: Saved to conversation memory")
    
    state["response"] = response_text
    
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
