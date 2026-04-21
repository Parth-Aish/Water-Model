import os
import json
import requests
import time

os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')

# First, let's test the fixed mapping locally
import joblib
import numpy as np

model_full = joblib.load('saved_models/XGBoost_SMOTE_Final.joblib')
scaler_full = joblib.load('saved_models/StandardScaler.joblib')
encoder = joblib.load('saved_models/LabelEncoder.joblib')

print('Testing Fixed Minimal Model Mapping:')
print('='*70)

test_cases = [
    ([3, 5000, 120], 'Extremely Acidic pH=3, Max EC=5000, High NO3=120'),
    ([7.5, 1200, 40], 'Normal Good Water pH=7.5, EC=1200, NO3=40'),
    ([5.2, 3500, 200], 'Acidic pH=5.2, High EC=3500, High NO3=200'),
    ([14, 5000, 500], 'Alkaline pH=14, Max EC=5000, Max NO3=500'),
    ([2, 100, 500], 'Very Acidic pH=2, Low EC=100, Max NO3=500'),
]

for features, description in test_cases:
    try:
        pH, EC, NO3 = features
        
        # Apply the mapping logic
        ec_factor = min(1.0, EC / 1000.0)
        total_hardness = 100 + (ec_factor * 300)
        ca = 30 + (ec_factor * 100)
        mg = 15 + (ec_factor * 70)
        cl = 50 + (ec_factor * 200)
        so4 = 40 + (ec_factor * 150)
        f = 0.5 + (ec_factor * 0.8)
        
        full_features = np.array([[pH, EC, total_hardness, ca, mg, cl, so4, NO3, f]])
        
        # Predict
        scaled_input = scaler_full.transform(full_features)
        pred_idx = model_full.predict(scaled_input)[0]
        pred_proba = model_full.predict_proba(scaled_input)[0]
        label = encoder.inverse_transform([pred_idx])[0]
        confidence = float(np.max(pred_proba)) * 100
        
        print(f'Input (3-sensor): {features}')
        print(f'Mapped (9-sensor): [pH={pH:.1f}, EC={EC:.0f}, TH={total_hardness:.1f}, Ca={ca:.1f}, Mg={mg:.1f}, Cl={cl:.1f}, SO4={so4:.1f}, NO3={NO3:.0f}, F={f:.1f}]')
        print(f'Description: {description}')
        print(f'Prediction: {label} ({confidence:.2f}%)')
        print()
    except Exception as e:
        print(f'ERROR: {str(e)}')
        print()
