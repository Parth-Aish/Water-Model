import os
import numpy as np
import joblib

os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')

model_full = joblib.load('saved_models/XGBoost_SMOTE_Final.joblib')
scaler_full = joblib.load('saved_models/StandardScaler.joblib')
encoder = joblib.load('saved_models/LabelEncoder.joblib')

print('Testing Improved Minimal Model Mapping:')
print('='*90)

test_cases = [
    ([3, 5000, 120], 'Bad: Extremely Acidic pH=3, Max EC=5000, High NO3=120'),
    ([7.5, 1200, 40], 'Good: Normal pH=7.5, EC=1200, NO3=40'),
    ([5.2, 3500, 200], 'Bad: Acidic pH=5.2, High EC=3500, High NO3=200'),
    ([7.5, 500, 10], 'Excellent: Normal pH, Low EC, Low NO3'),
    ([2, 6000, 500], 'Very Bad: Extreme pH=2, Very High EC=6000, Max NO3=500'),
]

for features, description in test_cases:
    pH, EC, NO3 = features
    
    # Apply improved mapping
    ec_percentile = min(1.0, max(0.0, (EC - 64) / 6610.0))
    no3_percentile = min(1.0, max(0.0, (NO3 - 0) / 2296.0))
    
    if EC < 500:
        total_hardness = 100 + (EC / 500 * 150)
    elif EC < 2000:
        total_hardness = 250 + ((EC - 500) / 1500 * 200)
    else:
        total_hardness = 450 + ((EC - 2000) / 5000 * 400)
    total_hardness = min(1200, total_hardness)
    
    ca = total_hardness * 0.25 + (no3_percentile * 50)
    mg = total_hardness * 0.15 + (no3_percentile * 30)
    cl = 50 + (ec_percentile * 200) + (no3_percentile * 100)
    so4 = 40 + (ec_percentile * 150) + (no3_percentile * 80)
    f = 0.5 + (ec_percentile * 1.0)
    
    full_features = np.array([[pH, EC, total_hardness, ca, mg, cl, so4, NO3, f]])
    
    # Predict
    scaled_input = scaler_full.transform(full_features)
    pred_idx = model_full.predict(scaled_input)[0]
    pred_proba = model_full.predict_proba(scaled_input)[0]
    label = encoder.inverse_transform([pred_idx])[0]
    confidence = float(np.max(pred_proba)) * 100
    
    print(f'\n{description}')
    print(f'Input (3-sensor): {features}')
    print(f'Mapped 9-sensor: TH={total_hardness:.0f}, Ca={ca:.0f}, Mg={mg:.0f}, Cl={cl:.0f}, SO4={so4:.0f}, F={f:.2f}')
    print(f'PREDICTION: {label.upper()} ({confidence:.1f}% confidence)')
