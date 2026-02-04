import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from app.logging_utils import setup_logger

# Load environment variables from .env file in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = setup_logger(__name__)

# Prompt variants for different conversation styles
PROMPT_VARIANTS = {
    "professional": """You are a professional assistant. Provide concise, technical, and direct answers.
Focus on facts and clarity. Use formal language.
Answer the user's question directly without extra elaboration.

User: {input}
Assistant:""",
    
    "friendly": """You are a warm and approachable assistant. Be conversational and personable.
Engage naturally with the user while remaining helpful.
Use simple language and explain concepts clearly.

User: {input}
Assistant:""",
    
    "minimal": """Keep your response very short and to the point.
One or two sentences only.

User: {input}
Assistant:"""
}

# Default prompt variant
DEFAULT_PROMPT_KEY = "professional"


class GeminiChainWrapper:
    """Wrapper to make Gemini work like a LangChain chain."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def invoke(self, inputs):
        """Invoke the model with the given input."""
        prompt_text = inputs.get("input", "")
        logger.info("-"*60)
        logger.info("GEMINI API CALL")
        logger.info(f"Prompt Length: {len(prompt_text)} characters")
        logger.info(f"Prompt Preview: {prompt_text[:150]}..." if len(prompt_text) > 150 else f"Prompt: {prompt_text}")
        
        response = self.model.generate_content(prompt_text)
        
        logger.info(f"Response Length: {len(response.text)} characters")
        logger.info(f"Response Preview: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
        logger.info("Gemini API call completed successfully")
        logger.info("-"*60)
        
        # Return object with content attribute for compatibility
        class Response:
            def __init__(self, text):
                self.content = text
        return Response(response.text)


def get_llm():
    """Initialize Google Gemini model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        raise ValueError("GEMINI_API_KEY environment variable is not set or still has placeholder value. Please configure it in .env file.")
    
    return GeminiChainWrapper(api_key)


def get_prompt_template(variant=DEFAULT_PROMPT_KEY):
    """Get a prompt template by variant name."""
    logger.info(f"Getting prompt template for variant: '{variant}'")
    prompt_text = PROMPT_VARIANTS.get(variant, PROMPT_VARIANTS[DEFAULT_PROMPT_KEY])
    
    if variant not in PROMPT_VARIANTS:
        logger.warning(f"Variant '{variant}' not found, using default '{DEFAULT_PROMPT_KEY}'")
    else:
        logger.info(f"Prompt template loaded successfully for variant '{variant}'")
    
    return PromptTemplate(
        input_variables=["input"],
        template=prompt_text
    )


def create_llm_chain():
    """Create a simple LLM chain for text generation."""
    logger.info("\n" + "="*60)
    logger.info("CREATING LLM CHAIN")
    logger.info("="*60)
    
    llm = get_llm()
    prompt = get_prompt_template()
    
    # Create a wrapper chain that applies prompt then calls llm
    class PromptLLMChain:
        def __init__(self, prompt_template, llm_model):
            self.prompt_template = prompt_template
            self.llm_model = llm_model
            logger.info("PromptLLMChain wrapper created")
        
        def invoke(self, inputs):
            """Format prompt and invoke LLM."""
            logger.info(f"\nFormatting prompt with inputs: {list(inputs.keys())}")
            formatted_prompt = self.prompt_template.format(**inputs)
            logger.info(f"Formatted prompt ready, invoking LLM...")
            response = self.llm_model.invoke({"input": formatted_prompt})
            logger.info("LLM invocation completed")
            return response
    
    logger.info("LLM chain created successfully")
    logger.info("="*60 + "\n")
    return PromptLLMChain(prompt, llm)
