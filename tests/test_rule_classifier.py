import os
import sys
os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')
sys.path.insert(0, '.')

# Import the rule-based function
import joblib
import numpy as np

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


print('Testing Rule-Based Water Quality Classifier:')
print('='*90)

test_cases = [
    # pH, EC, TH, Ca, Mg, Cl, SO4, NO3, F
    ([3, 5000, 700, 175, 105, 250, 200, 120, 1.3], 'BAD: Acidic pH=3, Very High EC, High minerals'),
    ([7.5, 1200, 350, 87, 52, 150, 100, 40, 0.8], 'NORMAL: Typical tapwater'),
    ([7.5, 300, 100, 30, 18, 60, 40, 5, 0.6], 'EXCELLENT: Clean water, low minerals'),
    ([7.5, 5000, 1200, 300, 180, 400, 300, 200, 1.5], 'TERRIBLE: Very high everything'),
    ([8.0, 1800, 450, 112, 68, 250, 150, 80, 0.9], 'POOR: High EC and minerals'),
]

descriptors = [
    'BAD: Acidic pH=3, Very High EC, High minerals',
    'NORMAL: Typical tapwater',
    'EXCELLENT: Clean water, low minerals',
    'TERRIBLE: Very high everything',
    'POOR: High EC and minerals',
]

for features, desc in test_cases:
    features_dict = {
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
    
    category, confidence, violations, warnings = predict_water_quality_rules(features_dict)
    
    print(f'\n{desc}')
    print(f'Prediction: {category.upper()} ({confidence:.1f}% confidence)')
    if warnings:
        for warning in warnings:
            print(f'  ⚠️ {warning}')
    else:
        print('  ✅ No warnings')
