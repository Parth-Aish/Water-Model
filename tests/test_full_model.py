import os
import joblib
import numpy as np

os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')

# Load models and scalers
model_full = joblib.load('saved_models/XGBoost_SMOTE_Final.joblib')
scaler_full = joblib.load('saved_models/StandardScaler.joblib')
encoder = joblib.load('saved_models/LabelEncoder.joblib')

print('Testing Full Model Predictions:')
print('='*70)

test_cases = [
    ([3, 5000, 2000, 500, 500, 1000, 500, 500, 10], 'TERRIBLE water - all max except pH'),
    ([7.5, 1200, 350, 70, 50, 150, 70, 40, 0.8], 'Normal good water'),
    ([5.2, 3500, 1200, 350, 220, 900, 400, 200, 2.5], 'Poor/Industrial water'),
    ([14, 5000, 2000, 500, 500, 1000, 500, 500, 10], 'TERRIBLE - all max'),
]

for features, description in test_cases:
    try:
        X = np.array([features], dtype=float)
        X_scaled = scaler_full.transform(X)
        
        pred_idx = model_full.predict(X_scaled)[0]
        pred_proba = model_full.predict_proba(X_scaled)[0]
        label = encoder.inverse_transform([pred_idx])[0]
        confidence = float(np.max(pred_proba)) * 100
        
        print(f'Description: {description}')
        print(f'Prediction: {label} ({confidence:.2f}%)')
        print(f'All probabilities: {dict(zip(encoder.classes_, np.round(pred_proba, 4)))}')
        print()
    except Exception as e:
        print(f'ERROR: {str(e)}')
        print()
