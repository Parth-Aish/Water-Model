import os
import joblib
import numpy as np

os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')

# Load models and scalers
model_minimal = joblib.load('saved_models/XGBoost_Minimal_3.joblib')
scaler_minimal = joblib.load('saved_models/StandardScaler_Minimal_3.joblib')
encoder = joblib.load('saved_models/LabelEncoder.joblib')

print('Testing Minimal Model Predictions:')
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
        X = np.array([features], dtype=float)
        print(f'Input shape: {X.shape}')
        X_scaled = scaler_minimal.transform(X)
        print(f'Scaled shape: {X_scaled.shape}')
        
        pred_idx = model_minimal.predict(X_scaled)[0]
        pred_proba = model_minimal.predict_proba(X_scaled)[0]
        label = encoder.inverse_transform([pred_idx])[0]
        confidence = float(np.max(pred_proba)) * 100
        
        print(f'Input: {features}')
        print(f'Description: {description}')
        print(f'Prediction: {label} ({confidence:.2f}%)')
        print()
    except Exception as e:
        print(f'ERROR: {str(e)}')
        print()
