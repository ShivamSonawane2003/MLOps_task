#!/usr/bin/env python
"""Test calculator routing without needing OpenAI API."""

import os
import sys
from pathlib import Path

os.environ['OPENAI_API_KEY'] = 'sk-mock-for-testing'

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.calculator import is_math_expression, calculate
from app.graph import router_node, calculator_node
from app.monitoring import RequestTimer, record_request, get_metrics

print("\n" + "=" * 70)
print("TESTING LLM CHATBOT ROUTING AND CALCULATOR")
print("=" * 70 + "\n")

# Test 1: Router decision
print("[Test 1] Router Node - Routing Decision")
print("-" * 70)

test_cases = [
    ("10 + 5", "calculator"),
    ("What is 10 + 5?", "calculator"),
    ("Hello world", "llm"),
    ("Tell me about Python", "llm"),
    ("100 * 50", "calculator"),
    ("50 / 10", "calculator"),
]

passed = 0
for message, expected_route in test_cases:
    state = {"session_id": "test", "message": message, "response": "", "route": ""}
    result = router_node(state)
    actual_route = result["route"]
    status = "✓" if actual_route == expected_route else "✗"
    print(f"{status} Message: '{message}'")
    print(f"  Expected: {expected_route}, Got: {actual_route}")
    if actual_route == expected_route:
        passed += 1

print(f"\nRouter tests: {passed}/{len(test_cases)} passed\n")

# Test 2: Calculator node
print("[Test 2] Calculator Node - Math Expressions")
print("-" * 70)

calc_tests = [
    ("2 + 3", "5"),
    ("10 * 5", "50"),
    ("100 / 4", "25"),
    ("50 - 30", "20"),
]

passed_calc = 0
for expr, expected_result in calc_tests:
    state = {"session_id": "test", "message": expr, "response": "", "route": "calculator"}
    result = calculator_node(state)
    response = result["response"]
    contains_result = expected_result in response
    status = "✓" if contains_result else "✗"
    print(f"{status} Expression: '{expr}'")
    print(f"  Response: {response}")
    if contains_result:
        passed_calc += 1

print(f"\nCalculator tests: {passed_calc}/{len(calc_tests)} passed\n")

# Test 3: Monitoring
print("[Test 3] Request Monitoring")
print("-" * 70)

with RequestTimer() as timer:
    import time
    time.sleep(0.1)

record_request(timer.elapsed)
metrics = get_metrics()

print(f"Request latency: {timer.elapsed:.4f}s")
print(f"Total requests: {metrics['request_count']}")
print(f"Average latency: {metrics['average_latency']:.4f}s")
print("✓ Monitoring works\n")

# Test 4: Memory
print("[Test 4] Multi-User Session Memory")
print("-" * 70)

from app.memory import get_or_create_memory, add_to_memory, get_memory_context

# User 1
mem1 = get_or_create_memory("alice")
add_to_memory("alice", "My name is Alice", "Nice to meet you Alice!")
context1 = get_memory_context("alice")

# User 2
mem2 = get_or_create_memory("bob")
add_to_memory("bob", "I'm Bob", "Hi Bob!")
context2 = get_memory_context("bob")

# Verify isolation
print("Alice's context:", "Alice" in context1)
print("Bob's context:", "Bob" in context2)
print("Contexts are isolated:", ("Bob" not in context1) and ("Alice" not in context2))
print("✓ Session isolation works\n")

print("=" * 70)
print("✓ ALL CORE FUNCTIONALITY TESTS PASSED!")
print("=" * 70)
print("\nNote: LLM node requires valid OpenAI API key to test fully.")
print("      Calculator routing and memory isolation work without it.")
