#!/usr/bin/env python
"""Test the API endpoints with sample requests."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*70)
    print("Testing Health Endpoint")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_calculator():
    """Test calculator routing."""
    print("\n" + "="*70)
    print("Testing Calculator Route")
    print("="*70)
    
    test_cases = [
        {"session_id": "calc_test", "message": "10 + 5"},
        {"session_id": "calc_test", "message": "100 * 50"},
        {"session_id": "calc_test", "message": "50 / 10"},
    ]
    
    for test in test_cases:
        print(f"\nSending: {test['message']}")
        response = requests.post(f"{BASE_URL}/chat", json=test)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response']}")
        else:
            print(f"Error: {response.text}")
        time.sleep(0.5)


def test_llm():
    """Test LLM routing."""
    print("\n" + "="*70)
    print("Testing LLM Route (requires valid API key)")
    print("="*70)
    
    test_cases = [
        {"session_id": "llm_test", "message": "Hello, how are you?"},
        {"session_id": "llm_test", "message": "What is Python?"},
    ]
    
    for test in test_cases:
        print(f"\nSending: {test['message']}")
        response = requests.post(f"{BASE_URL}/chat", json=test)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response'][:200]}...")
        else:
            print(f"Error: {response.text}")
        time.sleep(1)


def test_memory():
    """Test conversation memory."""
    print("\n" + "="*70)
    print("Testing Conversation Memory")
    print("="*70)
    
    session_id = "memory_test"
    
    # First message
    msg1 = {"session_id": session_id, "message": "My name is Alice"}
    print(f"\nMessage 1: {msg1['message']}")
    response = requests.post(f"{BASE_URL}/chat", json=msg1)
    if response.status_code == 200:
        print(f"Response: {response.json()['response'][:200]}...")
    
    time.sleep(1)
    
    # Second message (should remember name)
    msg2 = {"session_id": session_id, "message": "What is my name?"}
    print(f"\nMessage 2: {msg2['message']}")
    response = requests.post(f"{BASE_URL}/chat", json=msg2)
    if response.status_code == 200:
        print(f"Response: {response.json()['response'][:200]}...")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LLM CHATBOT API TESTS")
    print("="*70)
    
    try:
        # Test 1: Health check
        if not test_health():
            print("\n❌ Server not responding. Make sure it's running on port 8000.")
            exit(1)
        
        # Test 2: Calculator
        test_calculator()
        
        # Test 3: LLM (may fail if API key not set)
        try:
            test_llm()
        except Exception as e:
            print(f"\n⚠️  LLM test failed (expected if API key not configured): {e}")
        
        # Test 4: Memory
        try:
            test_memory()
        except Exception as e:
            print(f"\n⚠️  Memory test failed: {e}")
        
        print("\n" + "="*70)
        print("✓ API TESTS COMPLETED")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server. Make sure it's running:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
