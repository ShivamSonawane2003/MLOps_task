import re
from app.logging_utils import setup_logger

logger = setup_logger(__name__)


def is_math_expression(text):
    """Check if text is a math expression."""
    # Simple heuristic: contains numbers + operators
    has_numbers = any(c.isdigit() for c in text)
    has_operators = any(op in text for op in ['+', '-', '*', '/', '%', '**'])
    return has_numbers and has_operators


def evaluate_expression(text):
    """Safely evaluate a math expression."""
    try:
        # Remove spaces
        text = text.replace(" ", "")
        
        # Only allow numbers, operators, and parentheses
        if not re.match(r"^[\d\.\+\-\*/%\(\)\.]+$", text):
            logger.warning(f"Invalid expression format: {text}")
            return None
        
        # Evaluate
        result = eval(text)
        logger.info(f"Evaluated: {text} = {result}")
        return result
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return None


def calculate(user_input):
    """Process a math calculation request."""
    if not is_math_expression(user_input):
        return None
    
    # Extract numbers and operators
    result = evaluate_expression(user_input)
    
    if result is not None:
        return f"The result is {result}"
    else:
        return "I couldn't calculate that. Please try a valid math expression."
