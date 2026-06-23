import pandas as pd
import numpy as np

def calculate_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes a Building Performance Risk Score (0-100) based on weighted factors:
    - High EUI (25%)
    - High Carbon Intensity (20%)
    - High Operating Cost per sqft (20%)
    - Old HVAC System (10%)
    - Poor Insulation (10%)
    - Old Windows (5%)
    - No Recent Retrofit (10%)
    
    Categorizes risk:
    - 0-25: Low
    - 26-50: Medium
    - 51-75: High
    - 76-100: Critical
    """
    scored_df = df.copy()
    
    # Check if risk score and category are already present and populated
    # (So we don't overwrite pre-existing labels from Mode 1 if they are set, 
    # but we still calculate them for new/synthetic uploads)
    has_risk_cols = (
        'building_performance_risk_score' in df.columns and 
        'building_performance_risk_category' in df.columns and
        not df['building_performance_risk_score'].isna().all()
    )
    
    # 1. EUI Score (normalized within building type to be fair, fallback to overall)
    eui_scores = pd.Series(0.0, index=scored_df.index)
    for b_type, group in scored_df.groupby('building_type'):
        if len(group) > 5:
            p10 = group['eui'].quantile(0.10)
            p90 = group['eui'].quantile(0.90)
            if p90 > p10:
                eui_scores.loc[group.index] = ((group['eui'] - p10) / (p90 - p10) * 100).clip(0, 100)
            else:
                eui_scores.loc[group.index] = 50.0
        else:
            eui_scores.loc[group.index] = 50.0
            
    # 2. Carbon Score (normalized within building type)
    carbon_scores = pd.Series(0.0, index=scored_df.index)
    for b_type, group in scored_df.groupby('building_type'):
        if len(group) > 5:
            p10 = group['carbon_intensity'].quantile(0.10)
            p90 = group['carbon_intensity'].quantile(0.90)
            if p90 > p10:
                carbon_scores.loc[group.index] = ((group['carbon_intensity'] - p10) / (p90 - p10) * 100).clip(0, 100)
            else:
                carbon_scores.loc[group.index] = 50.0
        else:
            carbon_scores.loc[group.index] = 50.0
            
    # 3. Cost Score (normalized within building type)
    cost_scores = pd.Series(0.0, index=scored_df.index)
    for b_type, group in scored_df.groupby('building_type'):
        if len(group) > 5:
            p10 = group['cost_per_sqft'].quantile(0.10)
            p90 = group['cost_per_sqft'].quantile(0.90)
            if p90 > p10:
                cost_scores.loc[group.index] = ((group['cost_per_sqft'] - p10) / (p90 - p10) * 100).clip(0, 100)
            else:
                cost_scores.loc[group.index] = 50.0
        else:
            cost_scores.loc[group.index] = 50.0

    # 4. HVAC Age Score: linear scaling between 5 and 20 years
    hvac_age_scores = ((scored_df['hvac_age'] - 5) / 15 * 100).clip(0, 100)
    
    # 5. Insulation Score: Poor=100, Fair=60, Good=20, Excellent=0
    insulation_mapping = {'Poor': 100.0, 'Fair': 60.0, 'Good': 20.0, 'Excellent': 0.0}
    insulation_scores = scored_df['insulation_quality'].map(insulation_mapping).fillna(50.0)
    
    # 6. Window Score: Single Pane=100, Double Pane=30, Triple Pane=0
    window_mapping = {'Single Pane': 100.0, 'Double Pane': 30.0, 'Triple Pane': 0.0}
    window_scores = scored_df['window_type'].map(window_mapping).fillna(30.0)
    
    # 7. Retrofit Age Score: linear scaling between 3 and 15 years
    retrofit_age_scores = ((scored_df['years_since_retrofit'] - 3) / 12 * 100).clip(0, 100)
    
    # Calculate composite risk score
    calculated_scores = (
        0.25 * eui_scores +
        0.20 * carbon_scores +
        0.20 * cost_scores +
        0.10 * hvac_age_scores +
        0.10 * insulation_scores +
        0.05 * window_scores +
        0.10 * retrofit_age_scores
    ).round(1)
    
    # Determine main reason for risk
    reasons = []
    for idx, row in scored_df.iterrows():
        contrib = {
            'High Energy Intensity': eui_scores.loc[idx] * 0.25,
            'High Carbon Intensity': carbon_scores.loc[idx] * 0.20,
            'High Operating Cost': cost_scores.loc[idx] * 0.20,
            'Aging HVAC System': hvac_age_scores.loc[idx] * 0.10,
            'Substandard Insulation': insulation_scores.loc[idx] * 0.10,
            'Inefficient Window Glazing': window_scores.loc[idx] * 0.05,
            'No Recent Retrofits': retrofit_age_scores.loc[idx] * 0.10
        }
        max_contrib = max(contrib, key=contrib.get)
        # If the risk score is low, say 'N/A - Low Risk'
        if calculated_scores.loc[idx] <= 25:
            reasons.append('Low Risk')
        else:
            reasons.append(max_contrib)
            
    scored_df['main_risk_reason'] = reasons
    
    if has_risk_cols:
        # Keep existing risk values if they exist, but fill missing ones
        scored_df['building_performance_risk_score'] = scored_df['building_performance_risk_score'].fillna(calculated_scores)
    else:
        scored_df['building_performance_risk_score'] = calculated_scores
        
    # Classify risk score into category
    # Low: 0-25, Medium: 26-50, High: 51-75, Critical: 76-100
    conditions = [
        (scored_df['building_performance_risk_score'] <= 25),
        (scored_df['building_performance_risk_score'] <= 50),
        (scored_df['building_performance_risk_score'] <= 75),
        (scored_df['building_performance_risk_score'] > 75)
    ]
    categories = ['Low', 'Medium', 'High', 'Critical']
    
    calculated_categories = np.select(conditions, categories, default='Medium')
    
    if has_risk_cols:
        scored_df['building_performance_risk_category'] = scored_df['building_performance_risk_category'].fillna(pd.Series(calculated_categories, index=scored_df.index))
    else:
        scored_df['building_performance_risk_category'] = calculated_categories
        
    return scored_df
