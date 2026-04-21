import os
import numpy as np
import joblib
import pandas as pd

os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')

# Load the actual trained dataset
df = pd.read_csv('Water_Quality_Processed.csv')

# Get actual Poor and Excellent samples
excellent_samples = df[df['WQI_Category'] == 'Excellent'].head(3)
poor_samples = df[df['WQI_Category'] == 'Poor'].head(3)
very_poor_samples = df[df['WQI_Category'] == 'Very Poor'].head(3)

model_full = joblib.load('saved_models/XGBoost_SMOTE_Final.joblib')
scaler_full = joblib.load('saved_models/StandardScaler.joblib')
encoder = joblib.load('saved_models/LabelEncoder.joblib')

feature_cols = ['pH', 'EC', 'Total Hardness', 'Ca', 'Mg', 'Cl', 'SO4', 'NO3', 'F']

print('Testing with ACTUAL training samples:')
print('='*90)

for category, samples in [('EXCELLENT', excellent_samples), ('POOR', poor_samples), ('VERY POOR', very_poor_samples)]:
    print(f'\n{category} samples from training data:')
    for idx, row in samples.iterrows():
        X = row[feature_cols].values.reshape(1, -1)
        X_scaled = scaler_full.transform(X)
        pred_idx = model_full.predict(X_scaled)[0]
        pred_proba = model_full.predict_proba(X_scaled)[0]
        label = encoder.inverse_transform([pred_idx])[0]
        confidence = float(np.max(pred_proba)) * 100
        
        print(f'  Sample: EC={row["EC"]:.0f}, TH={row["Total Hardness"]:.0f}, NO3={row["NO3"]:.0f}')
        print(f'  Predicted: {label} ({confidence:.1f}%) | Actual: {row["WQI_Category"]}')
