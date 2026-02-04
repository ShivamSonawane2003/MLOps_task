from langchain.memory import ConversationBufferMemory
from app.logging_utils import setup_logger

logger = setup_logger(__name__)

# In-memory session storage: session_id -> ConversationBufferMemory
sessions = {}


def get_or_create_memory(session_id):
    """Get or create memory for a session."""
    if session_id not in sessions:
        sessions[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        logger.info(f"Created memory for session: {session_id}")
    
    return sessions[session_id]


def add_to_memory(session_id, user_input, ai_response):
    """Add user input and AI response to session memory."""
    memory = get_or_create_memory(session_id)
    memory.save_context(
        {"input": user_input},
        {"output": ai_response}
    )
    logger.info(f"Added message to session {session_id}")


def get_memory_context(session_id):
    memory = get_or_create_memory(session_id)
    return memory.buffer


def clear_session(session_id):
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Cleared memory for session: {session_id}")
