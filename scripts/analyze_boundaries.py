import os
import numpy as np
import joblib

os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')

model_full = joblib.load('saved_models/XGBoost_SMOTE_Final.joblib')
scaler_full = joblib.load('saved_models/StandardScaler.joblib')
encoder = joblib.load('saved_models/LabelEncoder.joblib')

print('Analyzing Model Decision Boundaries:')
print('='*90)

# Based on dataset statistics, let's try to find what makes it predict "Poor"
# From the data: POOR has EC~1505, NO3~42.84, TH~411

test_features = [
    # Simple poor-like water (from training stats)
    [7.7, 1505, 411, 102, 62, 202, 165, 42, 0.8],
    # Very poor-like water
    [7.7, 2898, 631, 157, 95, 355, 275, 91, 1.2],
    # Unsuitable-like water
    [7.7, 6782, 1275, 318, 191, 754, 580, 175, 1.5],
    # With very low hardness
    [7.7, 1505, 100, 25, 15, 202, 165, 42, 0.8],
]

descriptions = [
    'Poor-like (from training stats)',
    'Very Poor-like (from training stats)',
    'Unsuitable-like (from training stats)',
    'Same but with LOW hardness'
]

for features, desc in zip(test_features, descriptions):
    X = np.array([features])
    scaled = scaler_full.transform(X)
    pred_idx = model_full.predict(scaled)[0]
    pred_proba = model_full.predict_proba(scaled)[0]
    label = encoder.inverse_transform([pred_idx])[0]
    confidence = float(np.max(pred_proba)) * 100
    
    print(f'\n{desc}')
    print(f'Features: {features}')
    print(f'PREDICTION: {label} ({confidence:.1f}%)')
