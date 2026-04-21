"""
🌊 WATER QUALITY PREDICTION API - ALL-IN-ONE LAUNCHER
=====================================================
This single file starts everything:
✅ Loads all trained models
✅ Starts the Flask API server
✅ Opens the web UI automatically in your browser
=====================================================
Just run: python run.py
"""

import threading
import time
import webbrowser
import os
import sys

# Ensure we're in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import Flask and other dependencies
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import numpy as np

print("\n" + "="*70)
print("🌊 WATER QUALITY PREDICTION API - STARTING UP")
print("="*70)

# ============================================
# INITIALIZE FLASK APP
# ============================================
print("\n📦 Initializing Flask application...")
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# ============================================
# LOAD TRAINED MODELS AND SCALERS
# ============================================
print("📦 Loading trained models...")
try:
    model_full = joblib.load("saved_models/XGBoost_SMOTE_Final.joblib")
    scaler_full = joblib.load("saved_models/StandardScaler.joblib")
    model_minimal = joblib.load("saved_models/XGBoost_Minimal_3.joblib")
    scaler_minimal = joblib.load("saved_models/StandardScaler_Minimal_3.joblib")
    encoder = joblib.load("saved_models/LabelEncoder.joblib")
    print("✅ All models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    sys.exit(1)

# ============================================
# ENDPOINT 0: SERVE HOME PAGE
# ============================================
@app.route('/', methods=['GET'])
def home():
    """Serve the web UI"""
    return send_file('static/index.html', mimetype='text/html')

# ============================================
# HELPER FUNCTION: SAFETY RULES
# ============================================
def apply_safety_rules(features, model_type, ml_label, ml_confidence):
    """
    Applies strict WHO/EPA safety boundaries.
    If the water violates fundamental safety parameters, 
    override the ML model's prediction.
    """
    if model_type == 'minimal':
        pH, EC, NO3 = features
    else:
        pH, EC, TH, Ca, Mg, Cl, SO4, NO3, F = features
        
    violations = 0
    severe_violations = 0
    
    # pH checks (WHO optimal: 6.5-8.5)
    if pH < 5.0 or pH > 10.0:
        severe_violations += 1
    elif pH < 6.5 or pH > 8.5:
        violations += 1
        
    # EC checks (µS/cm)
    if EC > 3000:
        severe_violations += 1
    elif EC > 1500:
        violations += 1
        
    # NO3 checks (mg/L, EPA limit: 10)
    if NO3 > 100:
        severe_violations += 1
    elif NO3 > 50:
        violations += 1
        
    if model_type == 'full':
        # TH checks
        if TH > 1000: severe_violations += 1
        elif TH > 500: violations += 1
        
        # F checks
        if F > 4.0: severe_violations += 1
        elif F > 1.5: violations += 1
        
    # Override logic
    if severe_violations > 0 or violations >= 2:
        return "Unsuitable", 99.9, "Unsafe"
    elif violations == 1:
        if ml_label in ['Excellent', 'Good']:
            return "Poor", 85.0, "Unsafe"
            
    safety = "Safe" if ml_label in ['Good', 'Excellent'] else "Unsafe"
    return ml_label, ml_confidence, safety


# ============================================
# ENDPOINT 1: FULL 9-SENSOR PREDICTION
# ============================================
@app.route('/predict/full', methods=['POST'])
def predict_full():
    """
    Expects JSON with 9 features:
    {
        "features": [pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F]
    }
    """
    try:
        data = request.json
        if 'features' not in data:
            return jsonify({'status': 'error', 'message': 'Missing "features" in request'}), 400
        
        features = data['features']
        if len(features) != 9:
            return jsonify({
                'status': 'error', 
                'message': f'Expected 9 features, got {len(features)}. Order: pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F'
            }), 400
        
        query_array = np.array(features).reshape(1, -1)
        scaled_input = scaler_full.transform(query_array)
        pred_idx = model_full.predict(scaled_input)[0]
        pred_proba = model_full.predict_proba(scaled_input)[0]
        
        ml_label = encoder.inverse_transform([pred_idx])[0]
        ml_confidence = float(np.max(pred_proba)) * 100
        
        label, confidence, safety = apply_safety_rules(features, 'full', ml_label, ml_confidence)
        
        return jsonify({
            'status': 'success',
            'model': 'Full 9-Sensor Array',
            'prediction': label,
            'confidence': f"{confidence:.2f}%",
            'safety': safety,
            'uid': '23BAI70459'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 2: MINIMAL 3-SENSOR PREDICTION
# ============================================
@app.route('/predict/minimal', methods=['POST'])
def predict_minimal():
    """
    Expects JSON with 3 features:
    {
        "features": [pH, EC, NO3]
    }
    """
    try:
        data = request.json
        if 'features' not in data:
            return jsonify({'status': 'error', 'message': 'Missing "features" in request'}), 400
        
        features = data['features']
        if len(features) != 3:
            return jsonify({
                'status': 'error', 
                'message': f'Expected 3 features, got {len(features)}. Order: pH, EC, NO3'
            }), 400
        
        query_array = np.array(features).reshape(1, -1)
        scaled_input = scaler_minimal.transform(query_array)
        pred_idx = model_minimal.predict(scaled_input)[0]
        pred_proba = model_minimal.predict_proba(scaled_input)[0]
        
        ml_label = encoder.inverse_transform([pred_idx])[0]
        ml_confidence = float(np.max(pred_proba)) * 100
        
        label, confidence, safety = apply_safety_rules(features, 'minimal', ml_label, ml_confidence)
        
        return jsonify({
            'status': 'success',
            'model': 'Minimal 3-Sensor IoT',
            'prediction': label,
            'confidence': f"{confidence:.2f}%",
            'safety': safety,
            'uid': '23BAI70459'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 3: INFO & HELP
# ============================================
@app.route('/info', methods=['GET'])
def info():
    """Returns API information"""
    return jsonify({
        'status': 'success',
        'api_name': 'Water Quality Prediction API',
        'version': '2.0',
        'endpoints': {
            'full_model': {
                'url': '/predict/full',
                'method': 'POST',
                'features': 9,
                'order': 'pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F',
                'example': {
                    'features': [7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8]
                }
            },
            'minimal_model': {
                'url': '/predict/minimal',
                'method': 'POST',
                'features': 3,
                'order': 'pH, EC, NO3',
                'example': {
                    'features': [7.5, 1200, 40]
                }
            }
        }
    })


# ============================================
# ENDPOINT 4: HEALTH CHECK
# ============================================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': '🚀 API is running!'}), 200


# ============================================
# HELPER FUNCTION: OPEN BROWSER
# ============================================
def open_browser():
    """Open the web UI in the default browser after a delay"""
    time.sleep(2)  # Give server time to start
    print("\n🌐 Opening web browser...")
    webbrowser.open('http://127.0.0.1:5000')


# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 STARTING SERVER")
    print("="*70)
    
    # Start browser opener in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("\n📍 Web UI URL: http://127.0.0.1:5000")
    print("   (Browser should open automatically in a few seconds...)\n")
    print("📚 API Endpoints:")
    print("   GET  http://127.0.0.1:5000/              → Web UI")
    print("   GET  http://127.0.0.1:5000/health        → Health check")
    print("   GET  http://127.0.0.1:5000/info          → API documentation")
    print("   POST http://127.0.0.1:5000/predict/full  → Full 9-sensor prediction")
    print("   POST http://127.0.0.1:5000/predict/minimal → Minimal 3-sensor prediction")
    print("\n" + "="*70)
    print("⏹️  To stop the server, press CTRL+C in this terminal")
    print("="*70 + "\n")
    
    # Run the Flask app
    try:
        from werkzeug.serving import run_simple
        run_simple('127.0.0.1', 5000, app, use_debugger=False, use_reloader=False)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("Please check if port 5000 is already in use.")
        sys.exit(1)
