"""
Simple test script to verify Gradio interface components
"""
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

try:
    from app.gradio_chatbot import ChatbotInterface
    print("✓ Successfully imported ChatbotInterface")
    
    # Test initialization
    chatbot = ChatbotInterface()
    print("✓ Successfully initialized ChatbotInterface")
    
    # Test log functionality
    log_files = chatbot.get_available_logs()
    print(f"✓ Found {len(log_files)} log files")
    
    # Test nemoguardrails connection (optional)
    try:
        import requests
        response = requests.get(f"{chatbot.nemoguardrails_url}/v1/rails/configs", timeout=5)
        if response.status_code == 200:
            print("✓ Nemoguardrails server is accessible")
        else:
            print(f"⚠ Nemoguardrails server returned status {response.status_code}")
    except Exception as e:
        print(f"⚠ Cannot connect to nemoguardrails server: {e}")
    
    # Test Ollama connection (optional)
    try:
        response = requests.get(f"{chatbot.ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama server is accessible")
        else:
            print(f"⚠ Ollama server returned status {response.status_code}")
    except Exception as e:
        print(f"⚠ Cannot connect to Ollama server: {e}")
    
    print("\n🎉 All basic tests passed! The Gradio interface should work correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install gradio: pip install gradio")
except Exception as e:
    print(f"❌ Error: {e}")