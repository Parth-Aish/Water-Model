import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import f1_score

print("\n" + "="*70)
print("🔧 RETRAINING 3-SENSOR MODEL - FINAL FIX")
print("="*70 + "\n")

# Load data
df = pd.read_csv('Water_Quality_Processed.csv')
df.columns = df.columns.str.strip().str.replace(' ', '_')

# Prepare data for 3-sensor model
features_3 = ['pH', 'EC', 'NO3']
X = df[features_3]
le = LabelEncoder()
y = le.fit_transform(df['WQI_Category'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("📊 Class Distribution:")
for i, cls in enumerate(le.classes_):
    count = np.sum(y == i)
    print(f"   {cls:12} → {count:5} samples")

# Train with better hyperparameters
print("\n🏋️ Training new 3-sensor model with improved settings...")
model_3 = XGBClassifier(
    n_estimators=600,
    max_depth=8,
    learning_rate=0.06,
    subsample=0.95,
    colsample_bytree=0.95,
    min_child_weight=2,
    gamma=1,
    random_state=42,
    eval_metric='mlogloss'
)

model_3.fit(X_train, y_train, verbose=False)

# Evaluate
y_pred = model_3.predict(X_test)
f1 = f1_score(y_test, y_pred, average='weighted')
print(f"✅ F1-Score: {f1:.4f}\n")

# Test on actual data
print("🧪 Testing on actual training data samples:\n")
for class_idx in range(len(le.classes_)):
    class_name = le.classes_[class_idx]
    class_data = X[y == class_idx]
    
    if len(class_data) > 0:
        example = class_data.iloc[0].values.reshape(1, -1)
        pred = model_3.predict(example)[0]
        pred_name = le.inverse_transform([pred])[0]
        proba = model_3.predict_proba(example)[0]
        confidence = np.max(proba) * 100
        
        match = "✅" if pred_name == class_name else "❌"
        print(f"{match} {class_name:12} → Predicted: {pred_name:12} ({confidence:.1f}%)")

# Test user's polluted water input
print(f"\n🧪 Testing USER'S INPUT (pH=5.5, EC=4000, NO3=120):")
user_input = np.array([[5.5, 4000, 120]])
pred = model_3.predict(user_input)[0]
pred_name = le.inverse_transform([pred])[0]
proba = model_3.predict_proba(user_input)[0]
confidence = np.max(proba) * 100
print(f"   → Predicted: {pred_name} ({confidence:.1f}%)")

# Save the model
print("\n💾 Saving trained model...")
scaler_3 = StandardScaler()
scaler_3.fit(X_train)

joblib.dump(model_3, "saved_models/XGBoost_Minimal_3.joblib")
joblib.dump(scaler_3, "saved_models/StandardScaler_Minimal_3.joblib")
joblib.dump(le, "saved_models/LabelEncoder.joblib")

print("✅ Model saved successfully!\n")

print("="*70)
print("🔄 Now RESTART the API server to load the new model")
print("="*70 + "\n")
