import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from .logging_utils import setup_logger

# Load environment variables from .env file
load_dotenv()

logger = setup_logger(__name__)

# Prompt variants for different conversation styles
PROMPT_VARIANTS = {
    "professional": """You are a helpful assistant. Keep responses concise and professional.
Answer the user's question directly.

User: {input}
Assistant:""",
    
    "friendly": """You are a friendly and helpful assistant. Be conversational and approachable.
Keep responses clear and friendly.

User: {input}
Assistant:""",
    
    "minimal": """Answer concisely.

User: {input}
Assistant:"""
}

# Default prompt variant
DEFAULT_PROMPT_KEY = "professional"


def get_llm():
    """Initialize ChatOpenAI model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please configure it in .env file.")
    
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=500,
        api_key=api_key
    )


def get_prompt_template(variant=DEFAULT_PROMPT_KEY):
    """Get a prompt template by variant name."""
    prompt_text = PROMPT_VARIANTS.get(variant, PROMPT_VARIANTS[DEFAULT_PROMPT_KEY])
    return PromptTemplate(
        input_variables=["input"],
        template=prompt_text
    )


def create_llm_chain():
    """Create a simple LLM chain for text generation."""
    llm = get_llm()
    prompt = get_prompt_template()
    chain = prompt | llm
    logger.info("LLM chain created")
    return chain
