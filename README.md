# 💧 Water Quality Prediction API

A machine learning-powered web application for predicting water quality using AI models. This project provides an easy-to-use web interface and REST API for water quality assessment with two different prediction models.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Features

- **Two Prediction Models:**
  - 🔬 **Full Model (9 Sensors)**: Comprehensive analysis using 9 water quality parameters
  - ⚡ **Minimal Model (3 Sensors)**: Cost-efficient IoT solution using only 3 key parameters

- **Web Interface:**
  - 🎨 Beautiful, responsive UI with real-time validation
  - 📊 Color-coded results for quick assessment
  - 🔔 Input range validation and warnings
  - ⚙️ API status monitoring

- **Robust Backend:**
  - ✅ Input validation with range checking
  - 🚀 Fast predictions using XGBoost and scikit-learn
  - 🛡️ Error handling and informative error messages
  - 📊 Confidence scores for each prediction

- **API:**
  - 📍 REST endpoints for both models
  - 📚 Full API documentation
  - 🔌 Health check endpoint

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Usage](#usage)
4. [API Endpoints](#api-endpoints)
5. [Input Parameters](#input-parameters)
6. [Model Details](#model-details)
7. [Project Structure](#project-structure)
8. [Troubleshooting](#troubleshooting)
9. [License](#license)

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step 1: Clone or Download the Project

```bash
# Clone the repository (if using Git)
git clone <repository-url>
cd "Water Model"

# Or simply download and extract the ZIP file
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Model Files

Ensure the following files exist in the `saved_models/` directory:
- `XGBoost_SMOTE_Final.joblib` (Full model)
- `StandardScaler.joblib` (Full model scaler)
- `XGBoost_Minimal_3.joblib` (Minimal model)
- `StandardScaler_Minimal_3.joblib` (Minimal model scaler)
- `LabelEncoder.joblib` (Label encoder)

---

## ⚡ Quick Start

### Option 1: Run with Python (Recommended)

```bash
python run.py
```

This will:
1. Load all trained models
2. Start the Flask API server on `http://127.0.0.1:5000`
3. Automatically open the web UI in your default browser

### Option 2: Run with Batch File (Windows Only)

```bash
START.bat
```

### Option 3: Run with app.py

```bash
python app.py
```

---

## 💻 Usage

### Via Web Interface

1. **Open the Application**
   - Navigate to `http://127.0.0.1:5000` in your browser
   - You should see the API status indicator at the top

2. **Choose a Model**
   - **Full Model (9 Sensors)**: For comprehensive water analysis
   - **Minimal Model (3 Sensors)**: For quick IoT-based predictions

3. **Enter Water Quality Parameters**
   - Fill in the input fields with your measurements
   - The interface will highlight values outside recommended ranges
   - Default example values are pre-filled

4. **Get Predictions**
   - Click `🚀 Predict` or `⚡ Predict` button
   - View the results with confidence score and safety status
   - Check for any warning messages about out-of-range inputs

### Via API (using curl or Python)

#### Full Model Prediction

```bash
curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{
    "features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]
  }'
```

#### Minimal Model Prediction

```bash
curl -X POST http://127.0.0.1:5000/predict/minimal \
  -H "Content-Type: application/json" \
  -d '{
    "features": [7.5, 1200, 40]
  }'
```

#### Python Example

```python
import requests
import json

API_URL = "http://127.0.0.1:5000"

# Full model prediction
payload = {"features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]}
response = requests.post(f"{API_URL}/predict/full", json=payload)
print(response.json())

# Minimal model prediction
payload = {"features": [7.5, 1200, 40]}
response = requests.post(f"{API_URL}/predict/minimal", json=payload)
print(response.json())
```

---

## 📡 API Endpoints

### 1. Home Page
```
GET /
Returns: HTML web interface
```

### 2. Health Check
```
GET /health
Returns: {"status": "ok", "message": "🚀 API is running!"}
```

### 3. API Information
```
GET /info
Returns: API documentation with endpoint details
```

### 4. Full Model Prediction
```
POST /predict/full
Content-Type: application/json

Request:
{
  "features": [pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F]
}

Response:
{
  "status": "success",
  "model": "Full 9-Sensor Array",
  "prediction": "Excellent|Good|Poor|Very Poor",
  "confidence": "XX.XX%",
  "safety": "Safe|Unsafe",
  "uid": "23BAI70459"
}
```

### 5. Minimal Model Prediction
```
POST /predict/minimal
Content-Type: application/json

Request:
{
  "features": [pH, EC, NO3]
}

Response:
{
  "status": "success",
  "model": "Minimal 3-Sensor IoT",
  "prediction": "Excellent|Good|Poor|Very Poor",
  "confidence": "XX.XX%",
  "safety": "Safe|Unsafe",
  "uid": "23BAI70459"
}
```

---

## 📊 Input Parameters

### Full Model (9 Parameters)

| Parameter | Unit | Min | Max | Description |
|-----------|------|-----|-----|-------------|
| **pH** | - | 0 | 14 | Acidity/Alkalinity |
| **EC** | µS/cm | 0 | 5000 | Electrical Conductivity |
| **Total Hardness** | mg/L | 0 | 2000 | Calcium + Magnesium content |
| **Ca** | mg/L | 0 | 500 | Calcium concentration |
| **Mg** | mg/L | 0 | 500 | Magnesium concentration |
| **Cl** | mg/L | 0 | 1000 | Chloride concentration |
| **SO4** | mg/L | 0 | 500 | Sulfate concentration |
| **NO3** | mg/L | 0 | 500 | Nitrate concentration |
| **F** | mg/L | 0 | 10 | Fluoride concentration |

### Minimal Model (3 Parameters)

| Parameter | Unit | Min | Max | Description |
|-----------|------|-----|-----|-------------|
| **pH** | - | 0 | 14 | Acidity/Alkalinity |
| **EC** | µS/cm | 0 | 5000 | Electrical Conductivity |
| **NO3** | mg/L | 0 | 500 | Nitrate concentration |

---

## 🤖 Model Details

### Water Quality Classes

The models classify water into 4 categories:

| Class | Description | Safety |
|-------|-------------|--------|
| **Excellent** | Optimal water quality | Safe ✅ |
| **Good** | Acceptable water quality | Safe ✅ |
| **Poor** | Water needs treatment | Unsafe ⚠️ |
| **Very Poor** | Undrinkable water | Unsafe ⚠️ |

### Model Type

- **Algorithm**: XGBoost (Extreme Gradient Boosting)
- **Training Data**: Water Quality Dataset (balanced with SMOTE)
- **Confidence Score**: Probability of the predicted class (0-100%)

### Feature Scaling

- **Method**: StandardScaler (sklearn)
- **Application**: Features are scaled before prediction for optimal model performance

---

## 📁 Project Structure

```
Water Model/
├── app.py                          # Main Flask application
├── run.py                          # All-in-one launcher script
├── index.html                      # Web UI (frontend)
├── test_api.py                     # API testing script
├── retrain_model.py               # Model retraining script
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore file
├── README.md                      # This file
├── START.bat                      # Windows batch launcher
├── Water_Quality_Processed.csv    # Training dataset
├── Water Model.ipynb              # Main notebook
├── For Testing.ipynb              # Testing notebook
│
└── saved_models/                  # Trained models directory
    ├── XGBoost_SMOTE_Final.joblib
    ├── StandardScaler.joblib
    ├── XGBoost_Minimal_3.joblib
    ├── StandardScaler_Minimal_3.joblib
    ├── LabelEncoder.joblib
    └── RandomForest_SMOTE_Final.joblib
```

---

## 🐛 Troubleshooting

### Issue: "API is offline. Start the server first!"

**Solution**: 
1. Ensure the Flask server is running (run `python run.py`)
2. Check that the server is on `http://127.0.0.1:5000`
3. If using a different port, update the `API_URL` in `index.html`

```javascript
const API_URL = 'http://127.0.0.1:5000'; // Change if needed
```

### Issue: "Model file not found"

**Solution**:
1. Verify all model files are in `saved_models/` directory
2. Check file names match exactly (case-sensitive on Unix/Linux)
3. Ensure `joblib` is installed: `pip install joblib`

### Issue: "Expected 9 features, got X"

**Solution**:
1. Ensure you're sending exactly 9 features for the full model
2. Check the feature order: pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F
3. For minimal model, send exactly 3 features: pH, EC, NO3

### Issue: Inputs showing values outside range

**Solution**:
1. This is expected behavior - the model can handle out-of-range values
2. The interface will highlight them in orange
3. Consider adjusting your inputs if they seem unreasonable
4. Check the water quality guidelines for your region

### Issue: Port 5000 already in use

**Solution**:
1. Find what's using port 5000:
   ```bash
   # On Windows
   netstat -ano | findstr :5000
   
   # On macOS/Linux
   lsof -i :5000
   ```
2. Either kill the process or modify the port in `run.py`:
   ```python
   run_simple('127.0.0.1', 5001, app, ...)  # Use 5001 instead
   ```

### Issue: Python not found

**Solution**:
1. Ensure Python is installed: `python --version`
2. On macOS/Linux, use `python3` instead of `python`
3. Add Python to PATH (Windows users)

---

## 📝 Example Scenarios

### Scenario 1: Rural Water Source Testing
```json
{
  "features": [7.2, 450, 280, 55, 30, 80, 50, 25, 0.5]
}
```
Expected: Likely "Good" or "Excellent"

### Scenario 2: Industrial Wastewater
```json
{
  "features": [5.5, 3500, 1200, 350, 220, 900, 400, 200, 2.5]
}
```
Expected: Likely "Poor" or "Very Poor"

### Scenario 3: Treated Municipal Water
```json
{
  "features": [7.8, 1100, 320, 68, 45, 120, 60, 35, 0.7]
}
```
Expected: Likely "Excellent"

---

## 🔗 Dependencies

- **Flask**: Web framework for Python
- **Flask-CORS**: Cross-Origin Resource Sharing support
- **scikit-learn**: Machine learning library
- **XGBoost**: Gradient boosting framework
- **joblib**: Serialization library for models
- **NumPy**: Numerical computing library
- **Pandas**: Data manipulation library

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Add new features
- Improve documentation

---

## 📄 License

This project is open source and available under the MIT License.

---

## ✅ Verification Checklist

Before deployment, verify:
- [ ] All model files are present in `saved_models/`
- [ ] Python 3.8+ is installed
- [ ] All dependencies are installed: `pip install -r requirements.txt`
- [ ] Port 5000 is available
- [ ] Run `python run.py` successfully
- [ ] Web UI loads at `http://127.0.0.1:5000`
- [ ] Both prediction models work
- [ ] API responds with valid JSON

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review API endpoint documentation
3. Check console output for error messages
4. Test with the provided example values

---

## 🎓 Project Author

**Student ID**: 23BAI70459

---

## 📈 Future Enhancements

- [ ] Database integration for storing predictions
- [ ] User authentication
- [ ] Batch prediction support
- [ ] Mobile app version
- [ ] Real-time data streaming
- [ ] Advanced analytics dashboard
- [ ] Model version management
- [ ] Automated model retraining

---

## 🙏 Acknowledgments

- Built with Flask, scikit-learn, and XGBoost
- Water quality dataset from public sources
- Open source community

---

**Last Updated**: 2026-04-21
**Version**: 2.0
    "features": [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]
}
```

**Feature Order:**
1. pH
2. EC (Electrical Conductivity)
3. Total_Hardness
4. Ca (Calcium)
5. Mg (Magnesium)
6. Cl (Chloride)
7. SO4 (Sulfate)
8. NO3 (Nitrate)
9. F (Fluoride)

**Response:**
```json
{
    "status": "success",
    "model": "Full 9-Sensor Array",
    "prediction": "Good",
    "confidence": "95.23%",
    "safety": "Safe",
    "uid": "23BAI70459"
}
```

---

### Minimal 3-Sensor Prediction
**Endpoint:** `POST /predict/minimal`

**Request:**
```json
{
    "features": [7.5, 1200, 40]
}
```

**Feature Order:**
1. pH
2. EC (Electrical Conductivity)
3. NO3 (Nitrate)

**Response:**
```json
{
    "status": "success",
    "model": "Minimal 3-Sensor IoT",
    "prediction": "Good",
    "confidence": "87.45%",
    "safety": "Safe",
    "uid": "23BAI70459"
}
```

---

## Prediction Classes

The API returns one of these 5 water quality classifications:

| Class | Meaning | Safety |
|-------|---------|--------|
| **Excellent** | Best water quality | ✅ Safe |
| **Good** | Acceptable quality | ✅ Safe |
| **Poor** | Below standard | ⚠️ Unsafe |
| **Very Poor** | Severely contaminated | ⚠️ Unsafe |
| **Unsuitable** | Dangerous | ⚠️ Unsafe |

---

## Test Examples

### Example 1: Python with requests
```python
import requests

response = requests.post(
    "http://127.0.0.1:5000/predict/full",
    json={"features": [7.0, 500, 150, 40, 25, 80, 40, 5, 0.3]}
)
print(response.json())
```

### Example 2: cURL
```bash
curl -X POST http://127.0.0.1:5000/predict/full \
  -H "Content-Type: application/json" \
  -d '{"features": [7.0, 500, 150, 40, 25, 80, 40, 5, 0.3]}'
```

### Example 3: JavaScript/Fetch
```javascript
fetch('http://127.0.0.1:5000/predict/full', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({features: [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]})
})
.then(r => r.json())
.then(data => console.log(data))
```

---

## Requirements

Make sure you have these installed:
```bash
pip install flask flask-cors joblib scikit-learn xgboost numpy
```

---

## File Structure
```
Water Model/
├── app.py                           # Main API server
├── test_api.py                      # Test script
├── README.md                        # This file
├── Water_Quality_Processed.csv      # Training data (for reference)
└── saved_models/
    ├── XGBoost_SMOTE_Final.joblib
    ├── StandardScaler.joblib
    ├── XGBoost_Minimal_3.joblib
    ├── StandardScaler_Minimal_3.joblib
    └── LabelEncoder.joblib
```

---

## Troubleshooting

**Q: "Connection refused" error?**
- Make sure the server is running (`python app.py`)

**Q: "Features not matching" error?**
- Check you're sending the correct number of features
- For full model: 9 features
- For minimal model: 3 features

**Q: Always getting same prediction?**
- Models are now fixed! Try extreme values to see different classes

---

Made with ❤️ for Water Quality Monitoring
