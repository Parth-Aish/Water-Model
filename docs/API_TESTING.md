# 🧪 API Testing Guide

This file contains examples to test the Water Quality Prediction API.

## Prerequisites

- Server running on `http://127.0.0.1:5000`
- Python with `requests` library installed: `pip install requests`

## Test Examples

### Test 1: Check API Health

```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "🚀 API is running!"
}
```

---

### Test 2: Get API Information

```bash
curl http://127.0.0.1:5000/info
```

**Expected Response:**
```json
{
  "status": "success",
  "api_name": "Water Quality Prediction API",
  "version": "2.0",
  "endpoints": { ... }
}
```

---

### Test 3: Full Model - Excellent Water

```bash
curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{
    "features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "model": "Full 9-Sensor Array",
  "prediction": "Excellent",
  "confidence": "95.50%",
  "safety": "Safe",
  "uid": "23BAI70459"
}
```

---

### Test 4: Full Model - Poor Water

```bash
curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{
    "features": [5.2, 3500, 1200, 350, 220, 900, 400, 200, 2.5]
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "model": "Full 9-Sensor Array",
  "prediction": "Poor",
  "confidence": "88.20%",
  "safety": "Unsafe",
  "uid": "23BAI70459"
}
```

---

### Test 5: Minimal Model

```bash
curl -X POST http://127.0.0.1:5000/predict/minimal \
  -H "Content-Type: application/json" \
  -d '{
    "features": [7.5, 1200, 40]
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "model": "Minimal 3-Sensor IoT",
  "prediction": "Good",
  "confidence": "92.30%",
  "safety": "Safe",
  "uid": "23BAI70459"
}
```

---

### Test 6: Error Handling - Wrong Feature Count

```bash
curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{
    "features": [7.5, 1200, 350]
  }'
```

**Expected Response (Error):**
```json
{
  "status": "error",
  "message": "Expected 9 features, got 3. Order: pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F"
}
```

---

### Test 7: Error Handling - Missing Features

```bash
curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response (Error):**
```json
{
  "status": "error",
  "message": "Missing \"features\" in request..."
}
```

---

## Python Testing Script

```python
import requests
import json

API_URL = "http://127.0.0.1:5000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{API_URL}/health")
    print("Health Check:", response.json())

def test_info():
    """Test info endpoint"""
    response = requests.get(f"{API_URL}/info")
    print("API Info:", json.dumps(response.json(), indent=2))

def test_full_model():
    """Test full model prediction"""
    payload = {
        "features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]
    }
    response = requests.post(f"{API_URL}/predict/full", json=payload)
    print("Full Model Prediction:", response.json())

def test_minimal_model():
    """Test minimal model prediction"""
    payload = {
        "features": [7.5, 1200, 40]
    }
    response = requests.post(f"{API_URL}/predict/minimal", json=payload)
    print("Minimal Model Prediction:", response.json())

def test_error_handling():
    """Test error handling"""
    # Wrong feature count
    payload = {"features": [7.5, 1200]}
    response = requests.post(f"{API_URL}/predict/full", json=payload)
    print("Error Test (Wrong count):", response.json())
    
    # Non-numeric features
    payload = {"features": ["a", 1200, 350, 70, 50, 150, 70, 40, 0.8]}
    response = requests.post(f"{API_URL}/predict/full", json=payload)
    print("Error Test (Non-numeric):", response.json())

if __name__ == "__main__":
    print("🧪 Testing Water Quality Prediction API\n")
    
    test_health()
    print("\n" + "="*50 + "\n")
    
    test_info()
    print("\n" + "="*50 + "\n")
    
    test_full_model()
    print("\n" + "="*50 + "\n")
    
    test_minimal_model()
    print("\n" + "="*50 + "\n")
    
    test_error_handling()
    
    print("\n✅ All tests completed!")
```

---

## Running Tests

### Run All Tests with curl

```bash
# Test 1
curl http://127.0.0.1:5000/health

# Test 2
curl http://127.0.0.1:5000/info

# Test 3
curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{"features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]}'
```

### Run Python Tests

```bash
python test_api.py
```

---

## Endpoints Summary

| Endpoint | Method | Purpose | Expected Status |
|----------|--------|---------|-----------------|
| `/` | GET | Web UI | 200 |
| `/health` | GET | Health check | 200 |
| `/info` | GET | API documentation | 200 |
| `/predict/full` | POST | Full model prediction | 200 / 400 / 500 |
| `/predict/minimal` | POST | Minimal model prediction | 200 / 400 / 500 |

---

## Common Issues During Testing

### Issue: Connection refused
- **Cause**: Server not running
- **Solution**: Execute `python run.py`

### Issue: 404 Not Found
- **Cause**: Wrong endpoint URL
- **Solution**: Check endpoint path spelling

### Issue: 400 Bad Request
- **Cause**: Wrong JSON format or feature count
- **Solution**: Verify JSON structure and feature count

### Issue: 500 Server Error
- **Cause**: Model or scaler loading issue
- **Solution**: Check console for error message, verify model files exist

---

## Performance Testing

Test response time:

```bash
# Using curl with time measurement
time curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{"features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]}'
```

Expected response time: < 100ms

---

## Load Testing

Use `Apache Bench` or `wrk` for load testing:

```bash
# Apache Bench (10,000 requests, 10 concurrent)
ab -n 10000 -c 10 -p data.json -T application/json http://127.0.0.1:5000/predict/full
```

---

**Last Updated**: 2026-04-21
