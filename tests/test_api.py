"""
Test script to verify the API is working correctly.
Run this AFTER starting the API server.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Health Check:")
        print(f"   {response.json()}\n")
        return True
    except:
        print("❌ API is not running! Start the server first.\n")
        return False

def test_info():
    """Get API information"""
    response = requests.get(f"{BASE_URL}/info")
    print("📚 API Info:")
    print(f"   {json.dumps(response.json(), indent=2)}\n")

def test_full_model():
    """Test the 9-sensor model"""
    print("🧪 Testing 9-Sensor Model:")
    
    test_cases = [
        {
            "name": "Clean Water",
            "features": [7.0, 500, 150, 40, 25, 80, 40, 5, 0.3]
        },
        {
            "name": "Medium Quality",
            "features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]
        },
        {
            "name": "Polluted Water",
            "features": [5.5, 3500, 1000, 200, 180, 500, 250, 300, 5.0]
        }
    ]
    
    for test in test_cases:
        response = requests.post(
            f"{BASE_URL}/predict/full",
            json={"features": test["features"]}
        )
        result = response.json()
        print(f"\n   {test['name']}:")
        print(f"   → Prediction: {result['prediction']}")
        print(f"   → Confidence: {result['confidence']}")
        print(f"   → Safety: {result['safety']}")

def test_minimal_model():
    """Test the 3-sensor model"""
    print("\n\n🧪 Testing 3-Sensor Model:")
    
    test_cases = [
        {
            "name": "Clean Water",
            "features": [7.0, 500, 5]
        },
        {
            "name": "Medium Quality",
            "features": [7.5, 1200, 40]
        },
        {
            "name": "Polluted Water",
            "features": [5.5, 3500, 300]
        }
    ]
    
    for test in test_cases:
        response = requests.post(
            f"{BASE_URL}/predict/minimal",
            json={"features": test["features"]}
        )
        result = response.json()
        print(f"\n   {test['name']}:")
        print(f"   → Prediction: {result['prediction']}")
        print(f"   → Confidence: {result['confidence']}")
        print(f"   → Safety: {result['safety']}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 WATER QUALITY API TEST SUITE")
    print("=" * 60 + "\n")
    
    if not test_health():
        exit()
    
    test_info()
    test_full_model()
    test_minimal_model()
    
    print("\n\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
