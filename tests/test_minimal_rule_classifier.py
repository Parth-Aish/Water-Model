import os
import sys
os.chdir(r'c:\Users\Parth\OneDrive\Desktop\Water Model\Water Model')
sys.path.insert(0, '.')
import numpy as np

def predict_water_quality_rules(features_dict):
    """Rule-based water quality prediction"""
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
    
    if pH < 6.5 or pH > 8.5:
        violations += 2
        warnings_list.append(f"pH {pH} is outside optimal range (6.5-8.5)")
    elif pH < 7.0 or pH > 8.0:
        violations += 1
        warnings_list.append(f"pH {pH} is suboptimal (ideal: 7.0-8.0)")
    
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
    
    if SO4 < 150:
        so4_score = 0
    elif SO4 < 250:
        so4_score = 1
    else:
        so4_score = 2
        violations += 1
        warnings_list.append(f"SO4 {SO4} is elevated")
    
    if F > 4.0:
        violations += 3
        warnings_list.append(f"F {F} exceeds EPA limit")
    elif F > 2.0:
        violations += 2
        warnings_list.append(f"F {F} is elevated")
    
    total_score = ec_score + th_score + no3_score + cl_score + so4_score
    
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


print('Testing 3-Sensor Minimal Model with Rule-Based Classification:')
print('='*90)

test_cases = [
    ([3, 5000, 120], 'BAD: Extremely Acidic pH=3, Very High EC=5000, High NO3=120'),
    ([7.5, 1200, 40], 'NORMAL: Typical pH=7.5, EC=1200, NO3=40'),
    ([7.5, 500, 10], 'EXCELLENT: Clean water pH=7.5, Low EC=500, Low NO3=10'),
    ([6.0, 3500, 200], 'POOR: Low pH=6.0, High EC=3500, High NO3=200'),
]

for features, description in test_cases:
    pH, EC, NO3 = features
    
    # Apply intelligent mapping
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
    
    features_dict = {
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
    
    category, confidence, violations, warnings = predict_water_quality_rules(features_dict)
    
    print(f'\n{description}')
    print(f'Input (3-sensor): pH={pH}, EC={EC}, NO3={NO3}')
    print(f'Estimated 9-sensor: TH={total_hardness:.0f}, Ca={ca:.0f}, Mg={mg:.0f}, Cl={cl:.0f}, SO4={so4:.0f}, F={f:.2f}')
    print(f'PREDICTION: {category.upper()} ({confidence:.1f}% confidence)')
    if warnings:
        for warning in warnings:
            print(f'  ⚠️ {warning}')
