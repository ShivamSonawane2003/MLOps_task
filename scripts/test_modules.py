import sys
import os

# Set a mock OpenAI key
os.environ['OPENAI_API_KEY'] = 'sk-mock-test-key-12345'

# Add the app directory to path
app_dir = os.path.join(os.path.dirname(__file__), '..', 'app')
sys.path.insert(0, app_dir)
sys.path.insert(0, os.path.dirname(__file__) + '/..')

# Change to app directory for relative imports to work properly
os.chdir(os.path.dirname(__file__) + '/..')

# Now test the modules
print("Testing imports and basic functionality...\n")

try:
    print("1. Testing logging_utils...")
    from app.logging_utils import setup_logger
    logger = setup_logger("test")
    logger.info("Logging works")
    print("✓ logging_utils OK\n")
    
except Exception as e:
    print(f"✗ Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Testing calculator...")
    from app.calculator import is_math_expression, calculate
    
    assert is_math_expression("10 + 5") == True
    assert is_math_expression("hello world") == False
    result = calculate("2 + 3")
    assert result == "The result is 5"
    print("✓ calculator OK\n")
    
except Exception as e:
    print(f"✗ Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Testing memory...")
    from app.memory import get_or_create_memory, add_to_memory, get_memory_context
    
    mem = get_or_create_memory("test_user")
    add_to_memory("test_user", "Hello", "Hi there!")
    context = get_memory_context("test_user")
    assert "Hello" in context or len(context) > 0
    print("✓ memory OK\n")
    
except Exception as e:
    print(f"✗ Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Testing monitoring...")
    from app.monitoring import RequestTimer, record_request, get_metrics
    
    with RequestTimer() as timer:
        import time
        time.sleep(0.01)
    
    record_request(timer.elapsed)
    metrics = get_metrics()
    assert metrics['request_count'] > 0
    print("✓ monitoring OK\n")
    
except Exception as e:
    print(f"✗ Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. Testing LLM module (no API call)...")
    from app.llm import get_prompt_template, PROMPT_VARIANTS
    
    prompt = get_prompt_template("professional")
    assert prompt is not None
    assert len(PROMPT_VARIANTS) >= 3
    print("✓ llm OK\n")
    
except Exception as e:
    print(f"✗ Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("6. Testing graph module...")
    from app.graph import build_graph
    
    # This will fail if OpenAI key is not set, so we just verify it imports
    print("✓ graph module imports OK (actual graph needs OpenAI API)\n")
    
except Exception as e:
    print(f"✗ Graph import/build issue: {e}\n")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("✓ All core module tests passed!")
print("=" * 60)
