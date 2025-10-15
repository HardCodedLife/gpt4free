"""
Test script for Ollama provider integration with g4f.
Tests the g4f Provider class functionality, model fetching, and streaming.
"""

import asyncio
import sys
from pathlib import Path

# Fix Windows encoding issues
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path to import g4f
sys.path.insert(0, str(Path(__file__).parent.parent))

from g4f.Provider import Ollama


async def test_import():
    """Test that Ollama provider can be imported."""
    print("=" * 60)
    print("TEST 1: Import Ollama Provider")
    print("=" * 60)

    try:
        print(f"✓ Provider imported successfully")
        print(f"  - URL: {Ollama.url}")
        print(f"  - Working: {Ollama.working}")
        print(f"  - Supports stream: {Ollama.supports_stream}")
        print(f"  - Default model: {Ollama.default_model}")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


async def test_get_models():
    """Test fetching available models from Ollama server."""
    print("\n" + "=" * 60)
    print("TEST 2: Fetch Available Models")
    print("=" * 60)

    try:
        models = Ollama.get_models()
        print(f"✓ Successfully fetched {len(models)} model(s):")
        for model in models:
            print(f"  - {model}")
        return True
    except Exception as e:
        print(f"✗ Error fetching models: {e}")
        return False


async def test_simple_completion():
    """Test simple chat completion without streaming."""
    print("\n" + "=" * 60)
    print("TEST 3: Simple Completion (non-streaming)")
    print("=" * 60)

    try:
        messages = [
            {"role": "user", "content": "Say 'Hello from Ollama!' and nothing else."}
        ]

        response_text = ""
        async for chunk in Ollama.create_async_generator(
            model=Ollama.default_model,
            messages=messages,
            stream=False,
            timeout=30
        ):
            response_text += chunk

        print(f"✓ Response received:")
        print(f"  {response_text}")
        return True
    except Exception as e:
        print(f"✗ Error in simple completion: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_streaming_completion():
    """Test streaming chat completion."""
    print("\n" + "=" * 60)
    print("TEST 4: Streaming Completion")
    print("=" * 60)

    try:
        messages = [
            {"role": "user", "content": "Count from 1 to 5, one number per line."}
        ]

        print("Streaming response:")
        print("-" * 40)
        chunk_count = 0
        async for chunk in Ollama.create_async_generator(
            model=Ollama.default_model,
            messages=messages,
            stream=True,
            timeout=30
        ):
            print(chunk, end="", flush=True)
            chunk_count += 1

        print()
        print("-" * 40)
        print(f"✓ Received {chunk_count} chunk(s)")
        return True
    except Exception as e:
        print(f"✗ Error in streaming: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_system_message():
    """Test support for system messages."""
    print("\n" + "=" * 60)
    print("TEST 5: System Message Support")
    print("=" * 60)

    try:
        messages = [
            {"role": "system", "content": "You are a pirate. Always respond like a pirate."},
            {"role": "user", "content": "Hello! How are you?"}
        ]

        response_text = ""
        async for chunk in Ollama.create_async_generator(
            model=Ollama.default_model,
            messages=messages,
            stream=True,
            timeout=30
        ):
            response_text += chunk

        print(f"✓ Response received:")
        print(f"  {response_text}")
        return True
    except Exception as e:
        print(f"✗ Error with system message: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_conversation_history():
    """Test multi-turn conversation."""
    print("\n" + "=" * 60)
    print("TEST 6: Conversation History")
    print("=" * 60)

    try:
        messages = [
            {"role": "user", "content": "My name is Jetson. Say 'Hello from Ollama!' and nothing else."},
            {"role": "assistant", "content": "Hello from Ollama!"},
            {"role": "user", "content": "What's my name."}
        ]

        response_text = ""
        async for chunk in Ollama.create_async_generator(
            model=Ollama.default_model,
            messages=messages,
            stream=True,
            timeout=30
        ):
            response_text += chunk

        print(f"✓ Response received:")
        print(f"  {response_text}")
        return True
    except Exception as e:
        print(f"✗ Error in conversation: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_model_validation():
    """Test model validation with get_model()."""
    print("\n" + "=" * 60)
    print("TEST 7: Model Validation")
    print("=" * 60)

    try:
        # This should work
        valid_model = Ollama.get_model(Ollama.default_model)
        print(f"✓ Valid model accepted: {valid_model}")

        # Test with empty model (should use default)
        default_used = Ollama.get_model("")
        print(f"✓ Empty model uses default: {default_used}")

        return True
    except Exception as e:
        print(f"✗ Model validation error: {e}")
        return False


async def test_optional_parameters():
    """Test optional parameters like temperature, top_p."""
    print("\n" + "=" * 60)
    print("TEST 8: Optional Parameters")
    print("=" * 60)

    try:
        messages = [
            {"role": "user", "content": "Say 'Parameters work!' and nothing else."}
        ]

        response_text = ""
        async for chunk in Ollama.create_async_generator(
            model=Ollama.default_model,
            messages=messages,
            stream=False,
            timeout=30,
            temperature=0.7,
            top_p=0.9,
            max_tokens=50
        ):
            response_text += chunk

        print(f"✓ Response with parameters:")
        print(f"  {response_text}")
        return True
    except Exception as e:
        print(f"✗ Error with parameters: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "OLLAMA PROVIDER TEST SUITE")
    print("Testing g4f Provider integration")
    print("Server: http://100.92.194.37:11434\n")

    results = []

    # Run tests
    results.append(await test_import())
    results.append(await test_get_models())
    results.append(await test_simple_completion())
    results.append(await test_streaming_completion())
    results.append(await test_system_message())
    results.append(await test_conversation_history())
    results.append(await test_model_validation())
    results.append(await test_optional_parameters())

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total} tests")

    if passed == total:
        print("[PASS] All tests passed!")
        print("\n[OK] Ollama provider is working correctly")
        print("[OK] Ready to proceed to GUI integration (Phase 2)")
    else:
        print(f"[FAIL] {total - passed} test(s) failed")
        print("\nPlease fix the failing tests before proceeding.")

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
