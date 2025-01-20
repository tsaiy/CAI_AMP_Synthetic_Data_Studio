import requests
import json

BASE_URL = "http://localhost:8100"

def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

def test_use_cases():
    """Test getting use cases"""
    response = requests.get(f"{BASE_URL}/use-cases")
    print("Use Cases:", json.dumps(response.json(), indent=2))

def test_generation():
    """Test generation endpoint"""
    payload = {
        "use_case": "code_generation",
        "model_id": "anthropic.claude-v2",
        "num_questions": 2,
        "topics": ["python_basics"],
        "technique": "sft",
        "export_type": "local"
    }
    
    response = requests.post(
        f"{BASE_URL}/synthesis/generate",
        json=payload
    )
    print("Generation Result:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_health()
    test_use_cases()
    test_generation()