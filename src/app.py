from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ============================================
# LOAD TRAINED MODELS AND SCALERS
# ============================================
print("📦 Loading models...")

try:
    model_full = joblib.load("saved_models/XGBoost_SMOTE_Final.joblib")
    scaler_full = joblib.load("saved_models/StandardScaler.joblib")
    model_minimal = joblib.load("saved_models/XGBoost_Minimal_3.joblib")
    scaler_minimal = joblib.load("saved_models/StandardScaler_Minimal_3.joblib")
    encoder = joblib.load("saved_models/LabelEncoder.joblib")
    print("✅ Models loaded successfully!\n")
except FileNotFoundError as e:
    print(f"❌ Error: Model file not found: {e}")
    print("   Please ensure all model files are in the 'saved_models/' directory")
    raise
except Exception as e:
    print(f"❌ Error loading models: {e}")
    raise

# Feature constraints for validation
FEATURE_CONSTRAINTS = {
    'pH': {'min': 0, 'max': 14, 'index': 0},
    'EC': {'min': 0, 'max': 5000, 'index': 1},
    'Total_Hardness': {'min': 0, 'max': 2000, 'index': 2},
    'Ca': {'min': 0, 'max': 500, 'index': 3},
    'Mg': {'min': 0, 'max': 500, 'index': 4},
    'Cl': {'min': 0, 'max': 1000, 'index': 5},
    'SO4': {'min': 0, 'max': 500, 'index': 6},
    'NO3_full': {'min': 0, 'max': 500, 'index': 7},
    'F': {'min': 0, 'max': 10, 'index': 8},
    'NO3_minimal': {'min': 0, 'max': 500, 'index': 2}
}

def predict_water_quality_rules(features_dict):
    """
    Rule-based water quality prediction when model is unavailable.
    Based on WHO/EPA water quality standards and training data statistics.
    """
    pH = features_dict.get('pH', 7.0)
    EC = features_dict.get('EC', 1000)
    TH = features_dict.get('Total_Hardness', 300)
    Ca = features_dict.get('Ca', 100)
    Mg = features_dict.get('Mg', 50)
    Cl = features_dict.get('Cl', 150)
    SO4 = features_dict.get('SO4', 100)
    NO3 = features_dict.get('NO3', 50)
    F = features_dict.get('F', 1.0)
    
    violations = 0
    warnings_list = []
    
    # pH: Optimal 6.5-8.5 (training data shows most good/excellent are 7.2-7.9)
    if pH < 6.5 or pH > 8.5:
        violations += 2
        warnings_list.append(f"pH {pH} is outside optimal range (6.5-8.5)")
    elif pH < 7.0 or pH > 8.0:
        violations += 1
        warnings_list.append(f"pH {pH} is suboptimal (ideal: 7.0-8.0)")
    
    # EC: Higher EC indicates more dissolved minerals
    # Excellent: <500, Good: 500-1000, Poor: 1000-3000, Very Poor: >3000
    if EC < 500:
        ec_score = 0
    elif EC < 1000:
        ec_score = 1
    elif EC < 2000:
        ec_score = 2
        violations += 1
        warnings_list.append(f"EC {EC} indicates elevated mineral content")
    else:
        ec_score = 3
        violations += 2
        warnings_list.append(f"EC {EC} is very high, indicating pollution")
    
    # Total Hardness: WHO guideline <300 mg/L is acceptable
    # Excellent: <200, Good: 200-300, Poor: 300-500, Very Poor: >500
    if TH < 200:
        th_score = 0
    elif TH < 300:
        th_score = 1
    elif TH < 400:
        th_score = 2
        violations += 1
        warnings_list.append(f"Total Hardness {TH} indicates moderately hard water")
    else:
        th_score = 3
        violations += 2
        warnings_list.append(f"Total Hardness {TH} is very high")
    
    # NO3 (Nitrate): EPA limit 10 mg/L (health criterion)
    # Excellent: <5, Good: 5-20, Poor: 20-100, Very Poor: >100
    if NO3 < 5:
        no3_score = 0
    elif NO3 < 20:
        no3_score = 1
    elif NO3 < 50:
        no3_score = 2
        violations += 1
        warnings_list.append(f"NO3 {NO3} exceeds EPA health criterion")
    else:
        no3_score = 3
        violations += 2
        warnings_list.append(f"NO3 {NO3} is very high, indicating pollution")
    
    # Chloride: <250 mg/L (EPA secondary standard)
    if Cl < 100:
        cl_score = 0
    elif Cl < 200:
        cl_score = 0
    elif Cl < 350:
        cl_score = 1
        violations += 1
        warnings_list.append(f"Cl {Cl} is elevated")
    else:
        cl_score = 2
        violations += 2
        warnings_list.append(f"Cl {Cl} exceeds secondary standard")
    
    # Sulfate: <250 mg/L (EPA secondary standard)
    if SO4 < 150:
        so4_score = 0
    elif SO4 < 250:
        so4_score = 1
    else:
        so4_score = 2
        violations += 1
        warnings_list.append(f"SO4 {SO4} is elevated")
    
    # F (Fluoride): Optimal 0.7-1.0, EPA limit 4.0 mg/L
    if F > 4.0:
        violations += 3
        warnings_list.append(f"F {F} exceeds EPA limit")
    elif F > 2.0:
        violations += 2
        warnings_list.append(f"F {F} is elevated")
    
    # Calculate overall score
    total_score = ec_score + th_score + no3_score + cl_score + so4_score
    
    # Determine water quality category
    if violations >= 5 or total_score >= 12:
        category = 'Unsuitable'
        confidence = min(100, 70 + violations * 5)
    elif violations >= 4 or total_score >= 10:
        category = 'Very Poor'
        confidence = min(100, 60 + violations * 5)
    elif violations >= 2 or total_score >= 6:
        category = 'Poor'
        confidence = min(100, 50 + violations * 5)
    elif violations >= 1 or total_score >= 3:
        category = 'Good'
        confidence = min(100, 40 + (5 - violations) * 10)
    else:
        category = 'Excellent'
        confidence = min(100, 80 + (5 - total_score) * 3)
    
    return category, confidence, violations, warnings_list


def validate_features(features, model_type='full'):
    """Validate input features against constraints"""
    if model_type == 'full':
        feature_names = ['pH', 'EC', 'Total_Hardness', 'Ca', 'Mg', 'Cl', 'SO4', 'NO3_full', 'F']
        constraints_to_check = {k: v for k, v in FEATURE_CONSTRAINTS.items() if k != 'NO3_minimal'}
    else:
        feature_names = ['pH', 'EC', 'NO3_minimal']
        constraints_to_check = {
            'pH': FEATURE_CONSTRAINTS['pH'],
            'EC': FEATURE_CONSTRAINTS['EC'],
            'NO3_minimal': FEATURE_CONSTRAINTS['NO3_minimal']
        }
    
    warnings = []
    for i, (name, value) in enumerate(zip(feature_names, features)):
        constraint_key = name if name in constraints_to_check else name.replace('_full', '').replace('_minimal', '')
        if constraint_key in constraints_to_check:
            constraint = constraints_to_check[constraint_key]
            if value < constraint['min'] or value > constraint['max']:
                warnings.append(f"{name} = {value} is outside recommended range ({constraint['min']}-{constraint['max']})")
    
    return warnings

# ============================================
# ENDPOINT 0: SERVE HOME PAGE
# ============================================
@app.route('/', methods=['GET'])
def home():
    """Serve the web UI"""
    return send_file('index.html', mimetype='text/html')


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
        if not data or 'features' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing "features" in request. Expected JSON format: {"features": [...]}'
            }), 400
        
        features = data['features']
        
        # Validate feature count
        if len(features) != 9:
            return jsonify({
                'status': 'error',
                'message': f'Expected 9 features, got {len(features)}. Order: pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F'
            }), 400
        
        # Validate all features are numbers
        try:
            features = [float(f) for f in features]
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'All features must be valid numbers'
            }), 400
        
        # Check for out-of-range values
        warnings = validate_features(features, 'full')
        
        # Use rule-based classification (XGBoost model not working reliably)
        features_full = {
            'pH': features[0],
            'EC': features[1],
            'Total_Hardness': features[2],
            'Ca': features[3],
            'Mg': features[4],
            'Cl': features[5],
            'SO4': features[6],
            'NO3': features[7],
            'F': features[8]
        }
        
        label, confidence, violations, rule_warnings = predict_water_quality_rules(features_full)
        safety = "Safe" if label in ['Good', 'Excellent'] else "Unsafe"
        
        # Combine input validation warnings with rule warnings
        all_warnings = warnings + rule_warnings if warnings else rule_warnings
        
        return jsonify({
            'status': 'success',
            'model': 'Full 9-Sensor Array (Rule-Based)',
            'prediction': label,
            'confidence': f"{confidence:.1f}%",
            'safety': safety,
            'uid': '23BAI70459',
            'warnings': all_warnings if all_warnings else None
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


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
    
    Maps to full 9-feature input using intelligent defaults:
    [pH, EC, Total_Hardness, Ca, Mg, Cl, SO4, NO3, F]
    """
    try:
        data = request.json
        if not data or 'features' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing "features" in request. Expected JSON format: {"features": [...]}'
            }), 400
        
        features = data['features']
        
        # Validate feature count
        if len(features) != 3:
            return jsonify({
                'status': 'error',
                'message': f'Expected 3 features, got {len(features)}. Order: pH, EC, NO3'
            }), 400
        
        # Validate all features are numbers
        try:
            features = [float(f) for f in features]
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'All features must be valid numbers'
            }), 400
        
        # Check for out-of-range values
        warnings = validate_features(features, 'minimal')
        
        # Extract the 3 input features
        pH, EC, NO3 = features
        
        # Map to 9-feature space using realistic parameter correlation
        # Based on water quality dataset statistics:
        # - High EC (conductivity) typically correlates with high hardness and ions
        # - High NO3 (nitrate) indicates pollution
        # - Parameters scale proportionally with each other
        
        # Normalize EC and NO3 for scaling (based on training data statistics)
        ec_percentile = min(1.0, max(0.0, (EC - 64) / 6610.0))
        no3_percentile = min(1.0, max(0.0, (NO3 - 0) / 2296.0))
        
        # Estimate Total Hardness - strongly correlated with EC
        # Good water: ~250, Poor water: ~400, Very Poor: ~630
        if EC < 500:
            total_hardness = 100 + (EC / 500 * 150)
        elif EC < 2000:
            total_hardness = 250 + ((EC - 500) / 1500 * 200)
        else:
            total_hardness = 450 + ((EC - 2000) / 5000 * 400)
        total_hardness = min(1200, total_hardness)
        
        # Estimate Ca (Calcium) - typically 20-30% of hardness
        ca = total_hardness * 0.25 + (no3_percentile * 50)
        
        # Estimate Mg (Magnesium) - typically 15-20% of hardness
        mg = total_hardness * 0.15 + (no3_percentile * 30)
        
        # Estimate Cl (Chloride) - correlated with EC
        cl = 50 + (ec_percentile * 200) + (no3_percentile * 100)
        
        # Estimate SO4 (Sulfate) - also correlated with EC
        so4 = 40 + (ec_percentile * 150) + (no3_percentile * 80)
        
        # F (Fluoride) - relatively independent, but slightly increases with EC
        f = 0.5 + (ec_percentile * 1.0)
        
        # Construct full 9-feature array
        full_features = np.array([[pH, EC, total_hardness, ca, mg, cl, so4, NO3, f]])
        
        # Use rule-based classification (XGBoost model is not working reliably)
        features_full = {
            'pH': pH,
            'EC': EC,
            'Total_Hardness': total_hardness,
            'Ca': ca,
            'Mg': mg,
            'Cl': cl,
            'SO4': so4,
            'NO3': NO3,
            'F': f
        }
        
        label, confidence, violations, rule_warnings = predict_water_quality_rules(features_full)
        safety = "Safe" if label in ['Good', 'Excellent'] else "Unsafe"
        
        # Combine frontend and rule warnings
        all_warnings = warnings + rule_warnings if warnings else rule_warnings
        
        return jsonify({
            'status': 'success',
            'model': 'Minimal 3-Sensor IoT (Rule-Based)',
            'prediction': label,
            'confidence': f"{confidence:.1f}%",
            'safety': safety,
            'uid': '23BAI70459',
            'warnings': all_warnings if all_warnings else None,
            'note': 'Uses intelligent parameter estimation and rule-based classification'
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


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
# HEALTH CHECK
# ============================================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': '🚀 API is running!'}), 200


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 WATER QUALITY PREDICTION API")
    print("=" * 60)
    print("\n📍 WEB UI:  http://127.0.0.1:5000")
    print("   (Open this link in your browser)\n")
    print("📚 API Endpoints:")
    print("   GET  http://127.0.0.1:5000/              → Web UI")
    print("   GET  http://127.0.0.1:5000/health        → Health check")
    print("   GET  http://127.0.0.1:5000/info          → API documentation")
    print("   POST http://127.0.0.1:5000/predict/full  → Full 9-sensor prediction")
    print("   POST http://127.0.0.1:5000/predict/minimal → Minimal 3-sensor prediction")
    print("\n" + "=" * 60 + "\n")
    
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
