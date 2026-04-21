import os
import joblib

os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')

scaler_full = joblib.load('saved_models/StandardScaler.joblib')
scaler_minimal = joblib.load('saved_models/StandardScaler_Minimal_3.joblib')

print('Scaler Feature Count:')
print('='*50)
print(f'Full Scaler n_features: {scaler_full.n_features_in_}')
print(f'Minimal Scaler n_features: {scaler_minimal.n_features_in_}')
print()

if hasattr(scaler_full, 'feature_names_in_'):
    print(f'Full Scaler feature names: {list(scaler_full.feature_names_in_)}')
if hasattr(scaler_minimal, 'feature_names_in_'):
    print(f'Minimal Scaler feature names: {list(scaler_minimal.feature_names_in_)}')
